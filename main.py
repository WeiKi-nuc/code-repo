"""
代码片段仓库 - 主入口
"""
import tkinter as tk
from tkinter import ttk
from store import SnippetStore
from ui import UIManager


def main():
    """主函数"""
    # 创建主窗口
    root = tk.Tk()
    
    # 设置主题
    style = ttk.Style()
    style.theme_use('clam')
    
    # 创建数据存储
    store = SnippetStore("snippets.json")
    
    # 创建界面管理器
    app = UIManager(root, store)
    
    # 运行应用
    root.mainloop()


if __name__ == "__main__":
    main()
