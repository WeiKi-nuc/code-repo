"""
界面管理类
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyperclip
from typing import Callable, Optional, List
from snippet import Snippet
from store import SnippetStore
from highlighter import Highlighter


class Sidebar:
    """侧边栏组件"""
    
    def __init__(self, parent: tk.Widget, on_tag_select: Callable, on_favorite_filter: Callable):
        self.frame = ttk.LabelFrame(parent, text="标签筛选", padding=5)
        self.on_tag_select = on_tag_select
        self.on_favorite_filter = on_favorite_filter
        
        # 收藏筛选按钮
        self.fav_btn = ttk.Button(
            self.frame,
            text="⭐ 收藏",
            command=self._on_favorite_click
        )
        self.fav_btn.pack(fill='x', pady=(0, 5))
        
        # 全部按钮
        self.all_btn = ttk.Button(
            self.frame,
            text="📁 全部",
            command=lambda: self.on_tag_select(None)
        )
        self.all_btn.pack(fill='x', pady=(0, 5))
        
        # 标签列表
        self.tag_listbox = tk.Listbox(self.frame, height=20, selectmode='single')
        self.tag_listbox.pack(fill='both', expand=True)
        self.tag_listbox.bind('<<ListboxSelect>>', self._on_tag_select)
        
        self.tags: List[str] = []
    
    def _on_favorite_click(self):
        """点击收藏按钮"""
        self.tag_listbox.selection_clear(0, 'end')
        self.on_favorite_filter()
    
    def _on_tag_select(self, event):
        """选择标签"""
        selection = self.tag_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.tags):
                self.on_tag_select(self.tags[index])
    
    def update_tags(self, tags: List[str]):
        """更新标签列表"""
        self.tags = tags
        self.tag_listbox.delete(0, 'end')
        for tag in tags:
            self.tag_listbox.insert('end', f"🏷️ {tag}")


class SnippetList:
    """片段列表组件"""
    
    def __init__(self, parent: tk.Widget, on_select: Callable):
        self.frame = ttk.LabelFrame(parent, text="代码片段", padding=5)
        self.on_select = on_select
        
        # 搜索框
        self.search_frame = ttk.Frame(self.frame)
        self.search_frame.pack(fill='x', pady=(0, 5))
        
        self.snippets: List[Snippet] = []
        self.search_callback: Optional[Callable] = None
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(fill='x')
        self.search_entry.insert(0, "搜索...")
        self.search_entry.bind('<FocusIn>', self._on_search_focus_in)
        self.search_entry.bind('<FocusOut>', self._on_search_focus_out)
        self.search_var.trace('w', self._on_search)
        
        # 列表框
        self.listbox = tk.Listbox(self.frame, width=40, height=25, selectmode='single')
        self.listbox.pack(fill='both', expand=True)
        self.listbox.bind('<<ListboxSelect>>', self._on_select)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(self.listbox, command=self.listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.listbox.config(yscrollcommand=scrollbar.set)
    
    def _on_search_focus_in(self, event):
        """搜索框获得焦点"""
        if self.search_var.get() == "搜索...":
            self.search_var.set('')
    
    def _on_search_focus_out(self, event):
        """搜索框失去焦点"""
        if self.search_var.get() == '':
            self.search_var.set("搜索...")
    
    def _on_search(self, *args):
        """搜索"""
        keyword = self.search_var.get()
        if keyword == "搜索...":
            keyword = ""
        if self.search_callback:
            self.search_callback(keyword)
    
    def _on_select(self, event):
        """选择片段"""
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.snippets):
                self.on_select(self.snippets[index])
    
    def update_list(self, snippets: List[Snippet]):
        """更新列表"""
        self.snippets = snippets
        self.listbox.delete(0, 'end')
        for snippet in snippets:
            fav_mark = "⭐ " if snippet.is_favorite else "  "
            lang_mark = f"[{snippet.language}]"
            display = f"{fav_mark}{snippet.title} {lang_mark}"
            self.listbox.insert('end', display)
    
    def set_search_callback(self, callback: Callable):
        """设置搜索回调"""
        self.search_callback = callback


class EditorPane:
    """编辑器面板组件"""
    
    def __init__(self, parent: tk.Widget, store: SnippetStore):
        self.frame = ttk.LabelFrame(parent, text="编辑区", padding=5)
        self.store = store
        
        # 标题
        title_frame = ttk.Frame(self.frame)
        title_frame.pack(fill='x', pady=(0, 5))
        ttk.Label(title_frame, text="标题:").pack(side='left')
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(title_frame, textvariable=self.title_var)
        self.title_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))
        
        # 语言选择
        lang_frame = ttk.Frame(self.frame)
        lang_frame.pack(fill='x', pady=(0, 5))
        ttk.Label(lang_frame, text="语言:").pack(side='left')
        self.language_var = tk.StringVar(value='text')
        self.language_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.language_var,
            values=['text', 'python', 'javascript', 'java', 'html', 'css', 'sql'],
            state='readonly',
            width=15
        )
        self.language_combo.pack(side='left', padx=(5, 0))
        self.language_combo.bind('<<ComboboxSelected>>', self._on_language_change)
        
        # 收藏复选框
        self.favorite_var = tk.BooleanVar()
        self.favorite_check = ttk.Checkbutton(
            lang_frame,
            text="收藏",
            variable=self.favorite_var
        )
        self.favorite_check.pack(side='right')
        
        # 代码编辑器
        code_frame = ttk.Frame(self.frame)
        code_frame.pack(fill='both', expand=True, pady=(0, 5))
        
        self.code_text = tk.Text(code_frame, wrap='none', font=('Consolas', 11))
        self.code_text.pack(side='left', fill='both', expand=True)
        
        code_scroll = ttk.Scrollbar(code_frame, command=self.code_text.yview)
        code_scroll.pack(side='right', fill='y')
        self.code_text.config(yscrollcommand=code_scroll.set)
        
        # 高亮器
        self.highlighter = Highlighter(self.code_text)
        
        # 代码变更监听
        self.code_text.bind('<KeyRelease>', self._on_code_change)
        
        # 描述
        desc_frame = ttk.Frame(self.frame)
        desc_frame.pack(fill='x', pady=(0, 5))
        ttk.Label(desc_frame, text="描述:").pack(anchor='w')
        self.description_var = tk.StringVar()
        self.description_entry = ttk.Entry(desc_frame, textvariable=self.description_var)
        self.description_entry.pack(fill='x', pady=(2, 0))
        
        # 标签
        tags_frame = ttk.Frame(self.frame)
        tags_frame.pack(fill='x')
        ttk.Label(tags_frame, text="标签:").pack(side='left')
        self.tags_var = tk.StringVar()
        self.tags_entry = ttk.Entry(tags_frame, textvariable=self.tags_var)
        self.tags_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))
        ttk.Label(tags_frame, text="(用逗号分隔)").pack(side='left', padx=(5, 0))
        
        self.current_snippet: Optional[Snippet] = None
    
    def _on_language_change(self, event):
        """语言改变"""
        self._apply_highlight()
    
    def _on_code_change(self, event):
        """代码改变"""
        self._apply_highlight()
    
    def _apply_highlight(self):
        """应用语法高亮"""
        code = self.code_text.get('1.0', 'end-1c')
        language = self.language_var.get()
        self.highlighter.highlight(code, language)
    
    def load_snippet(self, snippet: Snippet):
        """加载片段到编辑器"""
        self.current_snippet = snippet
        self.title_var.set(snippet.title)
        self.language_var.set(snippet.language)
        self.code_text.delete('1.0', 'end')
        self.code_text.insert('1.0', snippet.code)
        self.description_var.set(snippet.description)
        self.tags_var.set(', '.join(snippet.tags))
        self.favorite_var.set(snippet.is_favorite)
        self._apply_highlight()
    
    def get_snippet(self) -> Optional[Snippet]:
        """从编辑器获取片段"""
        if not self.current_snippet:
            return None
        
        tags_str = self.tags_var.get()
        tags = [t.strip() for t in tags_str.split(',') if t.strip()]
        
        snippet = Snippet(
            id=self.current_snippet.id,
            title=self.title_var.get(),
            code=self.code_text.get('1.0', 'end-1c'),
            language=self.language_var.get(),
            description=self.description_var.get(),
            tags=tags,
            is_favorite=self.favorite_var.get(),
            created_at=self.current_snippet.created_at
        )
        return snippet
    
    def clear(self):
        """清空编辑器"""
        self.current_snippet = None
        self.title_var.set('')
        self.language_var.set('text')
        self.code_text.delete('1.0', 'end')
        self.description_var.set('')
        self.tags_var.set('')
        self.favorite_var.set(False)


class Toolbar:
    """工具栏组件"""
    
    def __init__(self, parent: tk.Widget, 
                 on_new: Callable, on_save: Callable, 
                 on_delete: Callable, on_copy: Callable,
                 on_export: Callable, on_import: Callable):
        self.frame = ttk.Frame(parent)
        
        self.new_btn = ttk.Button(self.frame, text="➕ 新建", command=on_new)
        self.new_btn.pack(side='left', padx=2)
        
        self.save_btn = ttk.Button(self.frame, text="💾 保存", command=on_save)
        self.save_btn.pack(side='left', padx=2)
        
        self.delete_btn = ttk.Button(self.frame, text="🗑️ 删除", command=on_delete)
        self.delete_btn.pack(side='left', padx=2)
        
        self.copy_btn = ttk.Button(self.frame, text="📋 复制", command=on_copy)
        self.copy_btn.pack(side='left', padx=2)
        
        ttk.Separator(self.frame, orient='vertical').pack(side='left', fill='y', padx=5)
        
        self.export_btn = ttk.Button(self.frame, text="📤 导出", command=on_export)
        self.export_btn.pack(side='left', padx=2)
        
        self.import_btn = ttk.Button(self.frame, text="📥 导入", command=on_import)
        self.import_btn.pack(side='left', padx=2)


class UIManager:
    """界面管理器"""
    
    def __init__(self, root: tk.Tk, store: SnippetStore):
        self.root = root
        self.store = store
        self.current_snippet: Optional[Snippet] = None
        
        self.root.title("代码片段仓库")
        self.root.geometry("1200x700")
        self.root.minsize(900, 500)
        
        # 主框架
        self.main_frame = ttk.Frame(root, padding=5)
        self.main_frame.pack(fill='both', expand=True)
        
        # 工具栏
        self.toolbar = Toolbar(
            self.main_frame,
            self.on_new,
            self.on_save,
            self.on_delete,
            self.on_copy,
            self.on_export,
            self.on_import
        )
        self.toolbar.frame.pack(fill='x', pady=(0, 5))
        
        # 内容区
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill='both', expand=True)
        
        # 配置列权重
        self.content_frame.columnconfigure(0, weight=0)  # 侧边栏
        self.content_frame.columnconfigure(1, weight=0)  # 列表
        self.content_frame.columnconfigure(2, weight=1)  # 编辑器
        self.content_frame.rowconfigure(0, weight=1)
        
        # 侧边栏
        self.sidebar = Sidebar(
            self.content_frame,
            self.on_tag_select,
            self.on_favorite_filter
        )
        self.sidebar.frame.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        
        # 片段列表
        self.snippet_list = SnippetList(self.content_frame, self.on_snippet_select)
        self.snippet_list.frame.grid(row=0, column=1, sticky='nsew', padx=(0, 5))
        self.snippet_list.set_search_callback(self.on_search)
        
        # 编辑器
        self.editor = EditorPane(self.content_frame, store)
        self.editor.frame.grid(row=0, column=2, sticky='nsew')
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief='sunken', anchor='w')
        self.status_bar.pack(fill='x', side='bottom')
        
        # 刷新数据
        self.refresh_all()
    
    def refresh_all(self):
        """刷新所有数据"""
        self.refresh_list()
        self.refresh_tags()
    
    def refresh_list(self, snippets: List[Snippet] = None):
        """刷新片段列表"""
        if snippets is None:
            snippets = self.store.get_all()
        self.snippet_list.update_list(snippets)
    
    def refresh_tags(self):
        """刷新标签列表"""
        tags = self.store.get_all_tags()
        self.sidebar.update_tags(tags)
    
    def show_message(self, message: str):
        """显示状态栏消息"""
        self.status_var.set(message)
        self.root.after(3000, lambda: self.status_var.set("就绪"))
    
    def on_new(self):
        """新建片段"""
        self.editor.clear()
        self.current_snippet = Snippet()
        self.editor.current_snippet = self.current_snippet
        self.show_message("新建片段")
    
    def on_save(self):
        """保存片段"""
        snippet = self.editor.get_snippet()
        if not snippet:
            return
        
        if not snippet.title.strip():
            messagebox.showwarning("警告", "标题不能为空")
            return
        
        if snippet.id in self.store.snippets:
            self.store.update(snippet)
            self.show_message("片段已更新")
        else:
            self.store.add(snippet)
            self.show_message("片段已创建")
        
        self.refresh_all()
    
    def on_delete(self):
        """删除片段"""
        snippet = self.editor.get_snippet()
        if not snippet or snippet.id not in self.store.snippets:
            messagebox.showwarning("警告", "请先选择一个片段")
            return
        
        if messagebox.askyesno("确认", f"确定要删除 '{snippet.title}' 吗？"):
            self.store.delete(snippet.id)
            self.editor.clear()
            self.refresh_all()
            self.show_message("片段已删除")
    
    def on_copy(self):
        """复制代码到剪贴板"""
        code = self.editor.code_text.get('1.0', 'end-1c')
        if code:
            pyperclip.copy(code)
            self.show_message("代码已复制到剪贴板")
        else:
            self.show_message("没有可复制的内容")
    
    def on_export(self):
        """导出数据"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            if self.store.export_to_file(filepath):
                self.show_message(f"数据已导出到 {filepath}")
            else:
                messagebox.showerror("错误", "导出失败")
    
    def on_import(self):
        """导入数据"""
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            if self.store.import_from_file(filepath):
                self.refresh_all()
                self.show_message("数据已导入")
            else:
                messagebox.showerror("错误", "导入失败")
    
    def on_search(self, keyword: str):
        """搜索"""
        if keyword:
            results = self.store.search(keyword)
            self.refresh_list(results)
        else:
            self.refresh_list()
    
    def on_tag_select(self, tag: Optional[str]):
        """选择标签"""
        if tag:
            snippets = self.store.get_by_tag(tag)
            self.refresh_list(snippets)
        else:
            self.refresh_list()
    
    def on_favorite_filter(self):
        """筛选收藏"""
        snippets = self.store.get_favorites()
        self.refresh_list(snippets)
    
    def on_snippet_select(self, snippet: Snippet):
        """选择片段"""
        self.current_snippet = snippet
        self.editor.load_snippet(snippet)
