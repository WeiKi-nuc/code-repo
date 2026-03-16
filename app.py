import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from core import Snippet, SnippetStore, Highlighter


class Sidebar:
    def __init__(self, parent, ui_manager):
        self.ui_manager = ui_manager
        self.frame = ttk.LabelFrame(parent, text="标签 & 筛选")
        
        ttk.Button(self.frame, text="全部", command=self.show_all).pack(fill="x", padx=5, pady=2)
        ttk.Button(self.frame, text="★ 收藏", command=self.show_favorites).pack(fill="x", padx=5, pady=2)
        
        ttk.Label(self.frame, text="标签:").pack(anchor="w", padx=5, pady=(10, 2))
        self.tags_listbox = tk.Listbox(self.frame, height=10)
        self.tags_listbox.pack(fill="both", expand=True, padx=5, pady=2)
        self.tags_listbox.bind('<<ListboxSelect>>', self.on_tag_select)
        
        ttk.Label(self.frame, text="搜索:").pack(anchor="w", padx=5, pady=(10, 2))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.frame, textvariable=self.search_var)
        self.search_entry.pack(fill="x", padx=5, pady=2)
        self.search_entry.bind("<KeyRelease>", self.on_search)
        
        self.frame.pack(side="left", fill="y", padx=5, pady=5)

    def update_tags(self):
        self.tags_listbox.delete(0, tk.END)
        all_tags = set()
        for snippet in self.ui_manager.store.snippets.values():
            for tag in snippet.tags:
                all_tags.add(tag)
        for tag in sorted(all_tags):
            self.tags_listbox.insert(tk.END, tag)

    def show_all(self):
        self.ui_manager.current_snippets = self.ui_manager.store.get_all()
        self.ui_manager.refresh_list()

    def show_favorites(self):
        self.ui_manager.current_snippets = self.ui_manager.store.get_favorites()
        self.ui_manager.refresh_list()

    def on_tag_select(self, event):
        selection = self.tags_listbox.curselection()
        if selection:
            tag = self.tags_listbox.get(selection[0])
            self.ui_manager.current_snippets = self.ui_manager.store.get_by_tag(tag)
            self.ui_manager.refresh_list()

    def on_search(self, event):
        keyword = self.search_var.get()
        if keyword:
            self.ui_manager.current_snippets = self.ui_manager.store.search(keyword)
        else:
            self.ui_manager.current_snippets = self.ui_manager.store.get_all()
        self.ui_manager.refresh_list()


class SnippetList:
    def __init__(self, parent, ui_manager):
        self.ui_manager = ui_manager
        self.frame = ttk.LabelFrame(parent, text="代码片段列表")
        
        self.listbox = tk.Listbox(self.frame, width=30)
        self.listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        
        self.frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    def update(self, snippets):
        self.listbox.delete(0, tk.END)
        for snippet in snippets:
            prefix = "★ " if snippet.is_favorite else ""
            self.listbox.insert(tk.END, f"{prefix}{snippet.title} ({snippet.language})")

    def on_select(self, event):
        selection = self.listbox.curselection()
        if selection:
            snippet = self.ui_manager.current_snippets[selection[0]]
            self.ui_manager.load_snippet(snippet)


class EditorPane:
    def __init__(self, parent, ui_manager):
        self.ui_manager = ui_manager
        self.frame = ttk.LabelFrame(parent, text="编辑器")
        
        form_frame = ttk.Frame(self.frame)
        form_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(form_frame, text="标题:").grid(row=0, column=0, sticky="w", pady=2)
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(form_frame, textvariable=self.title_var)
        self.title_entry.grid(row=0, column=1, sticky="ew", pady=2, padx=5)
        form_frame.columnconfigure(1, weight=1)
        
        ttk.Label(form_frame, text="语言:").grid(row=1, column=0, sticky="w", pady=2)
        self.language_var = tk.StringVar()
        languages = sorted(ui_manager.highlighter.get_languages())
        self.language_combo = ttk.Combobox(form_frame, textvariable=self.language_var, values=languages)
        self.language_combo.grid(row=1, column=1, sticky="ew", pady=2, padx=5)
        self.language_combo.bind("<<ComboboxSelected>>", self.on_language_change)
        
        ttk.Label(form_frame, text="标签:").grid(row=2, column=0, sticky="w", pady=2)
        self.tags_var = tk.StringVar()
        self.tags_entry = ttk.Entry(form_frame, textvariable=self.tags_var)
        self.tags_entry.grid(row=2, column=1, sticky="ew", pady=2, padx=5)
        
        self.favorite_var = tk.BooleanVar()
        self.favorite_check = ttk.Checkbutton(form_frame, text="收藏", variable=self.favorite_var)
        self.favorite_check.grid(row=3, column=1, sticky="w", pady=2, padx=5)
        
        ttk.Label(self.frame, text="代码:").pack(anchor="w", padx=5)
        self.code_text = tk.Text(self.frame, wrap="none", height=15)
        code_scroll_y = ttk.Scrollbar(self.frame, orient="vertical", command=self.code_text.yview)
        code_scroll_x = ttk.Scrollbar(self.frame, orient="horizontal", command=self.code_text.xview)
        self.code_text.configure(yscrollcommand=code_scroll_y.set, xscrollcommand=code_scroll_x.set)
        
        code_frame = ttk.Frame(self.frame)
        code_frame.pack(fill="both", expand=True, padx=5, pady=2)
        self.code_text.pack(side="left", fill="both", expand=True)
        code_scroll_y.pack(side="right", fill="y")
        code_scroll_x.pack(side="bottom", fill="x")
        
        ttk.Label(self.frame, text="描述:").pack(anchor="w", padx=5, pady=(5, 0))
        self.desc_text = tk.Text(self.frame, height=3)
        self.desc_text.pack(fill="x", padx=5, pady=2)
        
        self.frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

    def on_language_change(self, event):
        self.ui_manager.apply_highlight()


class Toolbar:
    def __init__(self, parent, ui_manager):
        self.ui_manager = ui_manager
        self.frame = ttk.Frame(parent)
        
        ttk.Button(self.frame, text="新建", command=self.new_snippet).pack(side="left", padx=2)
        ttk.Button(self.frame, text="保存", command=self.save_snippet).pack(side="left", padx=2)
        ttk.Button(self.frame, text="删除", command=self.delete_snippet).pack(side="left", padx=2)
        ttk.Button(self.frame, text="复制", command=self.copy_code).pack(side="left", padx=2)
        ttk.Button(self.frame, text="导入", command=self.import_snippets).pack(side="left", padx=2)
        ttk.Button(self.frame, text="导出", command=self.export_snippets).pack(side="left", padx=2)
        
        self.frame.pack(side="top", fill="x", padx=5, pady=2)

    def new_snippet(self):
        self.ui_manager.current_snippet = None
        self.ui_manager.editor.title_var.set("")
        self.ui_manager.editor.code_text.delete("1.0", "end")
        self.ui_manager.editor.language_var.set("text")
        self.ui_manager.editor.tags_var.set("")
        self.ui_manager.editor.desc_text.delete("1.0", "end")
        self.ui_manager.editor.favorite_var.set(False)
        self.ui_manager.show_message("已创建新片段")

    def save_snippet(self):
        snippet = self.ui_manager.get_current_snippet()
        if not snippet.title:
            messagebox.showwarning("提示", "请输入标题")
            return
        if not snippet.code.strip():
            messagebox.showwarning("提示", "代码不能为空")
            return
        
        if self.ui_manager.current_snippet:
            snippet.id = self.ui_manager.current_snippet.id
            snippet.created_at = self.ui_manager.current_snippet.created_at
            self.ui_manager.store.update(snippet)
        else:
            self.ui_manager.store.add(snippet)
        
        self.ui_manager.current_snippet = snippet
        self.ui_manager.refresh_all()
        self.ui_manager.show_message("保存成功")

    def delete_snippet(self):
        if not self.ui_manager.current_snippet:
            messagebox.showwarning("提示", "请先选择一个片段")
            return
        if messagebox.askyesno("确认", "确定要删除这个代码片段吗？"):
            self.ui_manager.store.delete(self.ui_manager.current_snippet.id)
            self.new_snippet()
            self.ui_manager.refresh_all()
            self.ui_manager.show_message("删除成功")

    def copy_code(self):
        code = self.ui_manager.editor.code_text.get("1.0", tk.END).strip()
        if code:
            self.ui_manager.root.clipboard_clear()
            self.ui_manager.root.clipboard_append(code)
            self.ui_manager.show_message("代码已复制到剪贴板")
        else:
            self.ui_manager.show_message("没有可复制的代码")

    def import_snippets(self):
        file_path = filedialog.askopenfilename(
            title="选择导入文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                imported = 0
                for k, v in data.items():
                    snippet = Snippet.from_dict(v)
                    self.ui_manager.store.snippets[snippet.id] = snippet
                    imported += 1
                self.ui_manager.store.save()
                self.ui_manager.refresh_all()
                self.ui_manager.show_message(f"成功导入 {imported} 个片段")
            except Exception as e:
                messagebox.showerror("错误", f"导入失败: {e}")

    def export_snippets(self):
        file_path = filedialog.asksaveasfilename(
            title="导出到文件",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            try:
                data = {k: v.to_dict() for k, v in self.ui_manager.store.snippets.items()}
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                self.ui_manager.show_message(f"已导出到 {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {e}")


class UIManager:
    def __init__(self, root):
        self.root = root
        self.store = SnippetStore()
        self.highlighter = Highlighter()
        self.current_snippet = None
        self.current_snippets = []
        
        self.root.title("代码片段仓库")
        self.root.geometry("1200x700")
        self.root.minsize(800, 500)
        
        self.toolbar = Toolbar(root, self)
        
        main_frame = ttk.Frame(root)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.sidebar = Sidebar(main_frame, self)
        self.snippet_list = SnippetList(main_frame, self)
        self.editor = EditorPane(main_frame, self)
        
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief="sunken")
        self.status_bar.pack(side="bottom", fill="x")
        
        self.current_snippets = self.store.get_all()
        self.refresh_all()
        self.show_message("就绪")

    def refresh_all(self):
        self.sidebar.update_tags()
        self.snippet_list.update(self.current_snippets)

    def refresh_list(self):
        self.snippet_list.update(self.current_snippets)

    def load_snippet(self, snippet):
        self.current_snippet = snippet
        self.editor.title_var.set(snippet.title)
        self.editor.language_var.set(snippet.language)
        self.editor.tags_var.set(", ".join(snippet.tags))
        self.editor.favorite_var.set(snippet.is_favorite)
        self.editor.desc_text.delete("1.0", tk.END)
        self.editor.desc_text.insert("1.0", snippet.description)
        self.apply_highlight()

    def apply_highlight(self):
        code = self.editor.code_text.get("1.0", tk.END)
        if self.current_snippet:
            language = self.editor.language_var.get() or self.current_snippet.language
        else:
            language = self.editor.language_var.get() or "text"
        self.highlighter.highlight(self.editor.code_text, code, language)

    def get_current_snippet(self):
        title = self.editor.title_var.get().strip()
        code = self.editor.code_text.get("1.0", tk.END)
        language = self.editor.language_var.get() or "text"
        description = self.editor.desc_text.get("1.0", tk.END).strip()
        tags_text = self.editor.tags_var.get()
        tags = [t.strip() for t in tags_text.split(",") if t.strip()]
        is_favorite = self.editor.favorite_var.get()
        
        snippet = Snippet(title, code, language, description, tags, is_favorite)
        return snippet

    def show_message(self, message):
        self.status_var.set(f"  {message}")


def main():
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam')
    app = UIManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()
