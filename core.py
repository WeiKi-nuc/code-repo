import json
import re
import os
from datetime import datetime


class Snippet:
    def __init__(self, title, code, language, description="", tags=None, is_favorite=False):
        self.id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.title = title
        self.code = code
        self.language = language
        self.description = description
        self.tags = tags if tags else []
        self.is_favorite = is_favorite
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def get_preview(self):
        lines = self.code.strip().split("\n")[:3]
        return "\n".join(lines)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "code": self.code,
            "language": self.language,
            "description": self.description,
            "tags": self.tags,
            "is_favorite": self.is_favorite,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @staticmethod
    def from_dict(data):
        snippet = Snippet.__new__(Snippet)
        snippet.id = data["id"]
        snippet.title = data["title"]
        snippet.code = data["code"]
        snippet.language = data["language"]
        snippet.description = data.get("description", "")
        snippet.tags = data.get("tags", [])
        snippet.is_favorite = data.get("is_favorite", False)
        snippet.created_at = data.get("created_at", datetime.now().isoformat())
        snippet.updated_at = data.get("updated_at", datetime.now().isoformat())
        return snippet


class SnippetStore:
    def __init__(self, db_path="snippets.json"):
        self.snippets = {}
        self.db_path = db_path
        self.load()

    def load(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.snippets = {k: Snippet.from_dict(v) for k, v in data.items()}
            except:
                self.snippets = {}
        else:
            self.snippets = {}

    def save(self):
        data = {k: v.to_dict() for k, v in self.snippets.items()}
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add(self, snippet):
        self.snippets[snippet.id] = snippet
        self.save()
        return snippet.id

    def delete(self, snippet_id):
        if snippet_id in self.snippets:
            del self.snippets[snippet_id]
            self.save()
            return True
        return False

    def update(self, snippet):
        if snippet.id in self.snippets:
            snippet.updated_at = datetime.now().isoformat()
            self.snippets[snippet.id] = snippet
            self.save()
            return True
        return False

    def get_all(self):
        return sorted(self.snippets.values(), key=lambda x: (not x.is_favorite, x.updated_at), reverse=True)

    def get_by_tag(self, tag):
        return [s for s in self.snippets.values() if tag in s.tags]

    def get_favorites(self):
        return [s for s in self.snippets.values() if s.is_favorite]

    def search(self, keyword):
        keyword = keyword.lower()
        results = []
        for snippet in self.snippets.values():
            if (keyword in snippet.title.lower() or
                keyword in snippet.code.lower() or
                keyword in snippet.language.lower() or
                keyword in snippet.description.lower() or
                any(keyword in t.lower() for t in snippet.tags)):
                results.append(snippet)
        return sorted(results, key=lambda x: (not x.is_favorite, x.updated_at), reverse=True)


class Highlighter:
    def __init__(self):
        self.language_patterns = {
            "python": {
                "keyword": r"\b(def|class|if|elif|else|for|while|return|import|from|try|except|with|as|pass|break|continue|and|or|not|in|is|None|True|False)\b",
                "string": r"(['\"])(?:(?=(\\?))\2.)*?\1",
                "comment": r"#.*",
                "builtin": r"\b(print|len|range|list|dict|set|tuple|int|str|float|bool)\b"
            },
            "javascript": {
                "keyword": r"\b(function|var|let|const|if|else|for|while|return|import|export|class|try|catch|async|await|new|this)\b",
                "string": r"(['\"])(?:(?=(\\?))\2.)*?\1",
                "comment": r"//.*|/\*[\s\S]*?\*/",
                "builtin": r"\b(console|document|window|Promise|Object|Array|String|Number|Boolean)\b"
            },
            "java": {
                "keyword": r"\b(public|private|protected|class|interface|static|void|if|else|for|while|return|try|catch|new|this)\b",
                "string": r"(['\"])(?:(?=(\\?))\2.)*?\1",
                "comment": r"//.*|/\*[\s\S]*?\*/",
                "builtin": r"\b(System|String|Integer|Boolean|ArrayList|HashMap)\b"
            },
            "html": {
                "tag": r"<[^>]+>",
                "string": r"['\"][^'\"]*['\"]",
                "comment": r"<!--[\s\S]*?-->"
            },
            "css": {
                "selector": r"[^{}]+\{",
                "property": r"[a-zA-Z-]+\s*:",
                "value": r":[^;]+;",
                "comment": r"/\*[\s\S]*?\*/"
            },
            "sql": {
                "keyword": r"\b(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE|AND|OR|JOIN|LEFT|RIGHT|INNER|OUTER|GROUP|ORDER|BY|HAVING|LIMIT|CREATE|TABLE|ALTER|DROP)\b",
                "string": r"(['\"])(?:(?=(\\?))\2.)*?\1",
                "comment": r"--.*"
            },
            "c": {
                "keyword": r"\b(int|char|float|double|if|else|for|while|return|void|struct|typedef|static|const)\b",
                "string": r"(['\"])(?:(?=(\\?))\2.)*?\1",
                "comment": r"//.*|/\*[\s\S]*?\*/",
                "builtin": r"\b(printf|scanf|malloc|free|sizeof)\b"
            }
        }

    def get_languages(self):
        return list(self.language_patterns.keys()) + ["text", "go", "ruby", "php"]

    def highlight(self, text_widget, code, language):
        text_widget.delete("1.0", "end")
        text_widget.insert("1.0", code)
        
        lang = language.lower()
        if lang not in self.language_patterns:
            return
        
        patterns = self.language_patterns[lang]
        
        for tag_name, pattern in patterns.items():
            text_widget.tag_configure(tag_name, foreground=self._get_color(tag_name))
            
            for match in re.finditer(pattern, code, re.IGNORECASE if lang == "sql" else 0):
                start = match.start()
                end = match.end()
                
                start_idx = self._index_from_pos(code, start)
                end_idx = self._index_from_pos(code, end)
                
                try:
                    text_widget.tag_add(tag_name, start_idx, end_idx)
                except:
                    pass

    def _get_color(self, tag):
        colors = {
            "keyword": "#0000FF",
            "string": "#008000",
            "comment": "#808080",
            "builtin": "#2B91AF",
            "tag": "#800000",
            "selector": "#800000",
            "property": "#FF0000",
            "value": "#0000FF"
        }
        return colors.get(tag, "#000000")

    def _index_from_pos(self, code, pos):
        lines = code[:pos].split("\n")
        line = len(lines)
        col = len(lines[-1])
        return f"{line}.{col}"
