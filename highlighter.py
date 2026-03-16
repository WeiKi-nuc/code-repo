"""
语法高亮类
"""
import re
import tkinter as tk
from typing import Dict, List, Tuple


class Highlighter:
    """语法高亮器"""
    
    # 语言关键字定义
    KEYWORDS = {
        'python': [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def',
            'del', 'elif', 'else', 'except', 'False', 'finally', 'for',
            'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
            'None', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
            'True', 'try', 'while', 'with', 'yield', 'async', 'await'
        ],
        'javascript': [
            'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger',
            'default', 'delete', 'do', 'else', 'export', 'extends', 'false',
            'finally', 'for', 'function', 'if', 'import', 'in', 'instanceof',
            'new', 'null', 'return', 'super', 'switch', 'this', 'throw',
            'true', 'try', 'typeof', 'var', 'void', 'while', 'with', 'let',
            'static', 'yield', 'await', 'async'
        ],
        'java': [
            'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch',
            'char', 'class', 'const', 'continue', 'default', 'do', 'double',
            'else', 'enum', 'extends', 'false', 'final', 'finally', 'float',
            'for', 'goto', 'if', 'implements', 'import', 'instanceof', 'int',
            'interface', 'long', 'native', 'new', 'null', 'package', 'private',
            'protected', 'public', 'return', 'short', 'static', 'strictfp',
            'super', 'switch', 'synchronized', 'this', 'throw', 'throws',
            'transient', 'true', 'try', 'void', 'volatile', 'while'
        ],
        'html': [
            'a', 'abbr', 'address', 'area', 'article', 'aside', 'audio', 'b',
            'base', 'bdi', 'bdo', 'blockquote', 'body', 'br', 'button',
            'canvas', 'caption', 'cite', 'code', 'col', 'colgroup', 'data',
            'datalist', 'dd', 'del', 'details', 'dfn', 'dialog', 'div', 'dl',
            'dt', 'em', 'embed', 'fieldset', 'figcaption', 'figure', 'footer',
            'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'head', 'header',
            'hgroup', 'hr', 'html', 'i', 'iframe', 'img', 'input', 'ins',
            'kbd', 'label', 'legend', 'li', 'link', 'main', 'map', 'mark',
            'math', 'menu', 'meta', 'meter', 'nav', 'noscript', 'object',
            'ol', 'optgroup', 'option', 'output', 'p', 'picture', 'pre',
            'progress', 'q', 'rp', 'rt', 'ruby', 's', 'samp', 'script',
            'section', 'select', 'slot', 'small', 'source', 'span', 'strong',
            'style', 'sub', 'summary', 'sup', 'svg', 'table', 'tbody', 'td',
            'template', 'textarea', 'tfoot', 'th', 'thead', 'time', 'title',
            'tr', 'track', 'u', 'ul', 'var', 'video', 'wbr', 'DOCTYPE'
        ],
        'sql': [
            'ADD', 'ALL', 'ALTER', 'AND', 'ANY', 'AS', 'ASC', 'AUTHORIZATION',
            'BACKUP', 'BEGIN', 'BETWEEN', 'BREAK', 'BROWSE', 'BULK', 'BY',
            'CASCADE', 'CASE', 'CHECK', 'CHECKPOINT', 'CLOSE', 'CLUSTERED',
            'COALESCE', 'COLLATE', 'COLUMN', 'COMMIT', 'COMPUTE', 'CONNECT',
            'CONSTRAINT', 'CONTAINS', 'CONTAINSTABLE', 'CONTINUE', 'CONVERT',
            'CREATE', 'CROSS', 'CURRENT', 'CURRENT_DATE', 'CURRENT_TIME',
            'CURRENT_TIMESTAMP', 'CURRENT_USER', 'CURSOR', 'DATABASE',
            'DBCC', 'DEALLOCATE', 'DECLARE', 'DEFAULT', 'DELETE', 'DENY',
            'DESC', 'DISK', 'DISTINCT', 'DISTRIBUTED', 'DOUBLE', 'DROP',
            'DUMP', 'ELSE', 'END', 'ERRLVL', 'ESCAPE', 'EXCEPT', 'EXEC',
            'EXECUTE', 'EXISTS', 'EXIT', 'EXTERNAL', 'FETCH', 'FILE',
            'FILLFACTOR', 'FOR', 'FOREIGN', 'FREETEXT', 'FREETEXTTABLE',
            'FROM', 'FULL', 'FUNCTION', 'GOTO', 'GRANT', 'GROUP', 'HAVING',
            'HOLDLOCK', 'IDENTITY', 'IDENTITY_INSERT', 'IDENTITYCOL', 'IF',
            'IN', 'INDEX', 'INNER', 'INSERT', 'INTERSECT', 'INTO', 'IS',
            'JOIN', 'KEY', 'KILL', 'LEFT', 'LIKE', 'LINENO', 'LOAD',
            'MERGE', 'NATIONAL', 'NOCHECK', 'NONCLUSTERED', 'NOT', 'NULL',
            'NULLIF', 'OF', 'OFF', 'OFFSETS', 'ON', 'OPEN', 'OPENDATASOURCE',
            'OPENQUERY', 'OPENROWSET', 'OPENXML', 'OPTION', 'OR', 'ORDER',
            'OUTER', 'OVER', 'PERCENT', 'PIVOT', 'PLAN', 'PRECISION',
            'PRIMARY', 'PRINT', 'PROC', 'PROCEDURE', 'PUBLIC', 'RAISERROR',
            'READ', 'READTEXT', 'RECONFIGURE', 'REFERENCES', 'REPLICATION',
            'RESTORE', 'RESTRICT', 'RETURN', 'REVERT', 'REVOKE', 'RIGHT',
            'ROLLBACK', 'ROWCOUNT', 'ROWGUIDCOL', 'RULE', 'SAVE', 'SCHEMA',
            'SECURITYAUDIT', 'SELECT', 'SEMANTICKEYPHRASETABLE',
            'SEMANTICSIMILARITYDETAILSTABLE', 'SEMANTICSIMILARITYTABLE',
            'SESSION_USER', 'SET', 'SETUSER', 'SHUTDOWN', 'SOME', 'STATISTICS',
            'SYSTEM_USER', 'TABLE', 'TABLESAMPLE', 'TEXTSIZE', 'THEN', 'TO',
            'TOP', 'TRAN', 'TRANSACTION', 'TRIGGER', 'TRUNCATE', 'TRY_CONVERT',
            'TSEQUAL', 'UNION', 'UNIQUE', 'UNPIVOT', 'UPDATE', 'UPDATETEXT',
            'USE', 'USER', 'VALUES', 'VARYING', 'VIEW', 'WAITFOR', 'WHEN',
            'WHERE', 'WHILE', 'WITH', 'WITHIN GROUP', 'WRITETEXT'
        ],
        'css': [
            'align-content', 'align-items', 'align-self', 'all', 'animation',
            'animation-delay', 'animation-direction', 'animation-duration',
            'animation-fill-mode', 'animation-iteration-count', 'animation-name',
            'animation-play-state', 'animation-timing-function', 'backface-visibility',
            'background', 'background-attachment', 'background-blend-mode',
            'background-clip', 'background-color', 'background-image',
            'background-origin', 'background-position', 'background-repeat',
            'background-size', 'border', 'border-bottom', 'border-bottom-color',
            'border-bottom-left-radius', 'border-bottom-right-radius',
            'border-bottom-style', 'border-bottom-width', 'border-collapse',
            'border-color', 'border-image', 'border-image-outset',
            'border-image-repeat', 'border-image-slice', 'border-image-source',
            'border-image-width', 'border-left', 'border-left-color',
            'border-left-style', 'border-left-width', 'border-radius',
            'border-right', 'border-right-color', 'border-right-style',
            'border-right-width', 'border-spacing', 'border-style', 'border-top',
            'border-top-color', 'border-top-left-radius', 'border-top-right-radius',
            'border-top-style', 'border-top-width', 'border-width', 'bottom',
            'box-shadow', 'box-sizing', 'caption-side', 'clear', 'clip',
            'color', 'column-count', 'column-fill', 'column-gap', 'column-rule',
            'column-rule-color', 'column-rule-style', 'column-rule-width',
            'column-span', 'column-width', 'columns', 'content', 'counter-increment',
            'counter-reset', 'cursor', 'direction', 'display', 'empty-cells',
            'filter', 'flex', 'flex-basis', 'flex-direction', 'flex-flow',
            'flex-grow', 'flex-shrink', 'flex-wrap', 'float', 'font',
            'font-family', 'font-size', 'font-size-adjust', 'font-stretch',
            'font-style', 'font-variant', 'font-weight', 'height', 'justify-content',
            'left', 'letter-spacing', 'line-height', 'list-style', 'list-style-image',
            'list-style-position', 'list-style-type', 'margin', 'margin-bottom',
            'margin-left', 'margin-right', 'margin-top', 'max-height', 'max-width',
            'min-height', 'min-width', 'opacity', 'order', 'outline', 'outline-color',
            'outline-offset', 'outline-style', 'outline-width', 'overflow',
            'overflow-x', 'overflow-y', 'padding', 'padding-bottom', 'padding-left',
            'padding-right', 'padding-top', 'page-break-after', 'page-break-before',
            'page-break-inside', 'perspective', 'perspective-origin', 'position',
            'quotes', 'resize', 'right', 'tab-size', 'table-layout', 'text-align',
            'text-align-last', 'text-decoration', 'text-decoration-color',
            'text-decoration-line', 'text-decoration-style', 'text-indent',
            'text-justify', 'text-overflow', 'text-shadow', 'text-transform',
            'top', 'transform', 'transform-origin', 'transform-style', 'transition',
            'transition-delay', 'transition-duration', 'transition-property',
            'transition-timing-function', 'vertical-align', 'visibility', 'white-space',
            'width', 'word-break', 'word-spacing', 'word-wrap', 'z-index'
        ]
    }
    
    # 颜色配置
    COLORS = {
        'keyword': '#0000FF',      # 蓝色
        'string': '#008000',       # 绿色
        'comment': '#808080',      # 灰色
        'number': '#FF0000',       # 红色
        'function': '#795E26',     # 棕色
    }
    
    def __init__(self, text_widget: tk.Text):
        self.text_widget = text_widget
        self._setup_tags()
    
    def _setup_tags(self):
        """设置文本标签样式"""
        for tag_name, color in self.COLORS.items():
            self.text_widget.tag_configure(tag_name, foreground=color)
    
    def highlight(self, code: str, language: str):
        """高亮代码"""
        # 清除所有标签
        for tag in self.COLORS.keys():
            self.text_widget.tag_remove(tag, '1.0', 'end')
        
        if language == 'text':
            return
        
        # 获取关键字列表
        keywords = self.KEYWORDS.get(language, [])
        
        lines = code.split('\n')
        for line_num, line in enumerate(lines, 1):
            self._highlight_line(line, line_num, language, keywords)
    
    def _highlight_line(self, line: str, line_num: int, language: str, keywords: List[str]):
        """高亮单行代码"""
        # 注释高亮
        if language in ['python']:
            comment_match = re.search(r'(#.*)$', line)
            if comment_match:
                start = f"{line_num}.{comment_match.start()}"
                end = f"{line_num}.{comment_match.end()}"
                self.text_widget.tag_add('comment', start, end)
        elif language in ['javascript', 'java', 'css']:
            comment_match = re.search(r'(//.*)$', line)
            if comment_match:
                start = f"{line_num}.{comment_match.start()}"
                end = f"{line_num}.{comment_match.end()}"
                self.text_widget.tag_add('comment', start, end)
        elif language == 'html':
            comment_match = re.search(r'(<!--.*?-->)', line)
            if comment_match:
                start = f"{line_num}.{comment_match.start()}"
                end = f"{line_num}.{comment_match.end()}"
                self.text_widget.tag_add('comment', start, end)
        elif language == 'sql':
            comment_match = re.search(r'(--.*)$', line)
            if comment_match:
                start = f"{line_num}.{comment_match.start()}"
                end = f"{line_num}.{comment_match.end()}"
                self.text_widget.tag_add('comment', start, end)
        
        # 字符串高亮
        string_pattern = r'("[^"]*"|\'[^\']*\')'
        for match in re.finditer(string_pattern, line):
            start = f"{line_num}.{match.start()}"
            end = f"{line_num}.{match.end()}"
            self.text_widget.tag_add('string', start, end)
        
        # 数字高亮
        number_pattern = r'\b\d+\.?\d*\b'
        for match in re.finditer(number_pattern, line):
            start = f"{line_num}.{match.start()}"
            end = f"{line_num}.{match.end()}"
            self.text_widget.tag_add('number', start, end)
        
        # 关键字高亮
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            for match in re.finditer(pattern, line, re.IGNORECASE if language == 'sql' else 0):
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()}"
                self.text_widget.tag_add('keyword', start, end)
        
        # 函数名高亮
        if language in ['python', 'javascript', 'java']:
            func_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
            for match in re.finditer(func_pattern, line):
                start = f"{line_num}.{match.start(1)}"
                end = f"{line_num}.{match.end(1)}"
                self.text_widget.tag_add('function', start, end)
        
        # HTML标签高亮
        if language == 'html':
            tag_pattern = r'<(/?)([a-zA-Z][a-zA-Z0-9]*)'
            for match in re.finditer(tag_pattern, line):
                start = f"{line_num}.{match.start(2)}"
                end = f"{line_num}.{match.end(2)}"
                self.text_widget.tag_add('keyword', start, end)
    
    def get_supported_languages(self) -> List[str]:
        """获取支持的语言列表"""
        return ['text', 'python', 'javascript', 'java', 'html', 'css', 'sql']
