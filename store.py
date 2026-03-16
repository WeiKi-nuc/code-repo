"""
数据存储管理类
"""
import json
import os
from typing import List, Dict, Optional
from snippet import Snippet


class SnippetStore:
    """代码片段数据存储类"""
    
    def __init__(self, db_path: str = "snippets.json"):
        self.db_path = db_path
        self.snippets: Dict[str, Snippet] = {}
        self.load()
    
    def load(self):
        """从JSON文件读取数据"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        snippet = Snippet.from_dict(item)
                        self.snippets[snippet.id] = snippet
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载数据失败: {e}")
                self.snippets = {}
    
    def save(self):
        """写入JSON文件"""
        try:
            data = [snippet.to_dict() for snippet in self.snippets.values()]
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            print(f"保存数据失败: {e}")
            return False
    
    def add(self, snippet: Snippet) -> Snippet:
        """添加新片段"""
        snippet.update_timestamp()
        self.snippets[snippet.id] = snippet
        self.save()
        return snippet
    
    def delete(self, snippet_id: str) -> bool:
        """删除片段"""
        if snippet_id in self.snippets:
            del self.snippets[snippet_id]
            self.save()
            return True
        return False
    
    def update(self, snippet: Snippet) -> bool:
        """更新片段"""
        if snippet.id in self.snippets:
            snippet.update_timestamp()
            self.snippets[snippet.id] = snippet
            self.save()
            return True
        return False
    
    def get(self, snippet_id: str) -> Optional[Snippet]:
        """获取单个片段"""
        return self.snippets.get(snippet_id)
    
    def get_all(self) -> List[Snippet]:
        """获取所有片段（收藏置顶，按更新时间倒序）"""
        snippets = list(self.snippets.values())
        # 收藏置顶，然后按更新时间倒序
        snippets.sort(key=lambda s: (not s.is_favorite, s.updated_at), reverse=True)
        return snippets
    
    def get_by_tag(self, tag: str) -> List[Snippet]:
        """按标签筛选"""
        return [s for s in self.snippets.values() if tag in s.tags]
    
    def get_favorites(self) -> List[Snippet]:
        """获取收藏片段"""
        return [s for s in self.snippets.values() if s.is_favorite]
    
    def search(self, keyword: str) -> List[Snippet]:
        """标题/内容/语言模糊匹配搜索"""
        keyword = keyword.lower()
        results = []
        for snippet in self.snippets.values():
            if (keyword in snippet.title.lower() or
                keyword in snippet.code.lower() or
                keyword in snippet.language.lower() or
                any(keyword in tag.lower() for tag in snippet.tags)):
                results.append(snippet)
        # 收藏置顶，按更新时间倒序
        results.sort(key=lambda s: (not s.is_favorite, s.updated_at), reverse=True)
        return results
    
    def get_all_tags(self) -> List[str]:
        """获取所有标签"""
        tags = set()
        for snippet in self.snippets.values():
            tags.update(snippet.tags)
        return sorted(list(tags))
    
    def export_to_file(self, filepath: str) -> bool:
        """导出到JSON文件"""
        try:
            data = [snippet.to_dict() for snippet in self.snippets.values()]
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            print(f"导出失败: {e}")
            return False
    
    def import_from_file(self, filepath: str) -> bool:
        """从JSON文件导入"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    snippet = Snippet.from_dict(item)
                    # 生成新ID避免冲突
                    snippet.id = None
                    self.snippets[snippet.id] = snippet
            self.save()
            return True
        except (json.JSONDecodeError, IOError) as e:
            print(f"导入失败: {e}")
            return False
