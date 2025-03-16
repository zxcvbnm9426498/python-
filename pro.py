#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from tkinterdnd2 import DND_FILES, TkinterDnD


def remove_comments_from_code(code, file_type='py'):
    """
    从代码中移除注释
    
    Args:
        code (str): 原始代码
        file_type (str): 文件类型，支持 'py', 'js', 'html', 'css'
        
    Returns:
        str: 移除注释后的代码
    """
    if file_type == 'py':
        # 处理Python多行注释 (''' 或 """)
        pattern = r'("""|\'\'\').*?\1'
        # re.DOTALL 使 . 匹配包括换行符在内的所有字符
        code = re.sub(pattern, '', code, flags=re.DOTALL)
        
        # 处理Python单行注释 (#)
        result = []
        lines = code.split('\n')
        in_string = False
        string_char = None
        
        for line in lines:
            new_line = ''
            i = 0
            while i < len(line):
                # 检查是否在字符串内
                if not in_string and (line[i] == '"' or line[i] == "'"):
                    in_string = True
                    string_char = line[i]
                    new_line += line[i]
                elif in_string and line[i] == string_char and (i == 0 or line[i-1] != '\\'):
                    in_string = False
                    new_line += line[i]
                elif not in_string and line[i] == '#':
                    # 遇到注释符号且不在字符串内，忽略后面的内容
                    break
                else:
                    new_line += line[i]
                i += 1
            
            # 添加非空行或包含代码的行
            if new_line.strip() or not line.lstrip().startswith('#'):
                result.append(new_line)
        
        return '\n'.join(result)
    
    elif file_type == 'js':
        # 处理JS多行注释 /* */
        pattern_multiline = r'/\*[\s\S]*?\*/'
        code = re.sub(pattern_multiline, '', code)
        
        # 处理JS单行注释 //
        result = []
        lines = code.split('\n')
        in_string = False
        string_char = None
        
        for line in lines:
            new_line = ''
            i = 0
            while i < len(line):
                # 检查是否在字符串内
                if not in_string and (line[i] == '"' or line[i] == "'" or line[i] == '`'):
                    in_string = True
                    string_char = line[i]
                    new_line += line[i]
                elif in_string and line[i] == string_char and (i == 0 or line[i-1] != '\\'):
                    in_string = False
                    new_line += line[i]
                elif not in_string and i < len(line) - 1 and line[i] == '/' and line[i+1] == '/':
                    # 遇到注释符号且不在字符串内，忽略后面的内容
                    break
                else:
                    new_line += line[i]
                i += 1
            
            # 添加非空行或包含代码的行
            if new_line.strip() or not (line.lstrip().startswith('//') or line.lstrip().startswith('/*')):
                result.append(new_line)
        
        return '\n'.join(result)
    
    elif file_type == 'html':
        # 处理HTML注释 <!-- -->
        pattern = r'<!--[\s\S]*?-->'
        code = re.sub(pattern, '', code)
        return code
    
    elif file_type == 'css':
        # 处理CSS注释 /* */
        pattern = r'/\*[\s\S]*?\*/'
        code = re.sub(pattern, '', code)
        return code
    
    else:
        # 默认情况下不做处理
        return code


def process_file(file_path, output_dir=None, supported_extensions=None):
    """
    处理单个文件，移除注释
    
    Args:
        file_path (str): 要处理的文件路径
        output_dir (str, optional): 输出目录，如果为None则覆盖原文件
        supported_extensions (dict, optional): 支持的文件扩展名及其对应的处理类型
        
    Returns:
        bool: 处理是否成功
    """
    if supported_extensions is None:
        supported_extensions = {
            '.py': 'py',
            '.js': 'js',
            '.html': 'html',
            '.htm': 'html',
            '.css': 'css'
        }
    
    try:
        # 获取文件扩展名
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # 检查是否支持该文件类型
        if ext not in supported_extensions:
            print(f"不支持的文件类型: {ext}")
            return False
        
        # 获取文件类型
        file_type = supported_extensions[ext]
        
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        cleaned_code = remove_comments_from_code(code, file_type)
        
        if output_dir:
            # 创建与原始文件相同的目录结构
            rel_path = os.path.basename(file_path)
            output_path = os.path.join(output_dir, rel_path)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        else:
            output_path = file_path
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_code)
        
        return True
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
        return False


def process_directory(dir_path, output_dir=None, recursive=True, file_types=None):
    """
    处理目录中的所有支持的文件
    
    Args:
        dir_path (str): 要处理的目录路径
        output_dir (str, optional): 输出目录
        recursive (bool): 是否递归处理子目录
        file_types (list, optional): 要处理的文件类型列表
        
    Returns:
        tuple: (成功处理的文件数, 处理失败的文件数)
    """
    if file_types is None:
        # 默认支持的文件类型
        supported_extensions = {
            '.py': 'py',
            '.js': 'js',
            '.html': 'html',
            '.htm': 'html',
            '.css': 'css'
        }
    else:
        # 根据用户选择的文件类型构建支持的扩展名字典
        supported_extensions = {}
        if 'py' in file_types:
            supported_extensions['.py'] = 'py'
        if 'js' in file_types:
            supported_extensions['.js'] = 'js'
        if 'html' in file_types:
            supported_extensions['.html'] = 'html'
            supported_extensions['.htm'] = 'html'
        if 'css' in file_types:
            supported_extensions['.css'] = 'css'
    
    success_count = 0
    fail_count = 0
    
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            # 获取文件扩展名
            _, ext = os.path.splitext(file)
            ext = ext.lower()
            
            # 检查是否是支持的文件类型
            if ext in supported_extensions:
                file_path = os.path.join(root, file)
                
                if output_dir:
                    # 创建相对路径以保持目录结构
                    rel_path = os.path.relpath(file_path, dir_path)
                    new_output_dir = os.path.join(output_dir, os.path.dirname(rel_path))
                    os.makedirs(new_output_dir, exist_ok=True)
                    output_path = os.path.join(output_dir, rel_path)
                else:
                    output_path = file_path
                
                if process_file(file_path, output_path if output_dir else None, supported_extensions):
                    success_count += 1
                else:
                    fail_count += 1
        
        if not recursive:
            break  # 如果不递归，则只处理顶层目录
    
    return success_count, fail_count


class CommentRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("交付壁垒制造工具(bz:择安网络)")
        self.root.geometry("600x500")
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#ccc")
        self.style.configure("TLabel", padding=6)
        self.style.configure("TCheckbutton", padding=6)
        self.style.configure("DropZone.TFrame", relief="solid", borderwidth=2)
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文件/目录选择区域
        select_frame = ttk.LabelFrame(main_frame, text="选择文件或目录", padding="10", style="DropZone.TFrame")
        select_frame.pack(fill=tk.X, pady=10)
        
        # 拖放提示标签
        self.drop_label = ttk.Label(select_frame, text="拖放文件或文件夹到这里", font=("", 10, "italic"))
        self.drop_label.pack(pady=5)
        
        button_frame = ttk.Frame(select_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="选择文件", command=self.select_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="选择目录", command=self.select_directory).pack(side=tk.LEFT, padx=5)
        
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(button_frame, textvariable=self.path_var, width=50)
        self.path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # 配置拖放
        self.setup_drop_target(select_frame)
        self.setup_drop_target(self.path_entry)
        
        # 选项区域
        options_frame = ttk.LabelFrame(main_frame, text="选项", padding="10")
        options_frame.pack(fill=tk.X, pady=10)
        
        self.recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="递归处理子目录", variable=self.recursive_var).pack(anchor=tk.W)
        
        # 文件类型选择区域
        file_types_frame = ttk.LabelFrame(options_frame, text="文件类型", padding="5")
        file_types_frame.pack(fill=tk.X, pady=5, anchor=tk.W)
        
        # 创建文件类型选择变量
        self.py_var = tk.BooleanVar(value=True)
        self.js_var = tk.BooleanVar(value=True)
        self.html_var = tk.BooleanVar(value=True)
        self.css_var = tk.BooleanVar(value=True)
        
        # 创建文件类型选择复选框
        ttk.Checkbutton(file_types_frame, text="Python (.py)", variable=self.py_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(file_types_frame, text="JavaScript (.js)", variable=self.js_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(file_types_frame, text="HTML (.html, .htm)", variable=self.html_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(file_types_frame, text="CSS (.css)", variable=self.css_var).pack(side=tk.LEFT, padx=5)
        
        self.output_mode_var = tk.StringVar(value="overwrite")
        ttk.Radiobutton(options_frame, text="覆盖原文件", variable=self.output_mode_var, value="overwrite").pack(anchor=tk.W)
        ttk.Radiobutton(options_frame, text="输出到新目录", variable=self.output_mode_var, value="new_dir").pack(anchor=tk.W)
        
        self.output_dir_frame = ttk.Frame(options_frame)
        self.output_dir_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.output_dir_frame, text="输出目录:").pack(side=tk.LEFT)
        
        self.output_dir_var = tk.StringVar()
        ttk.Entry(self.output_dir_frame, textvariable=self.output_dir_var, width=40).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(self.output_dir_frame, text="浏览...", command=self.select_output_dir).pack(side=tk.LEFT, padx=5)
        
        # 状态和进度区域
        status_frame = ttk.LabelFrame(main_frame, text="状态", padding="10")
        status_frame.pack(fill=tk.X, pady=10)
        
        self.status_var = tk.StringVar(value="准备就绪")
        ttk.Label(status_frame, textvariable=self.status_var).pack(anchor=tk.W)
        
        # 操作按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="开始处理", command=self.start_processing).pack(side=tk.RIGHT, padx=5)
        
        # 绑定输出模式变更事件
        self.output_mode_var.trace_add("write", self.update_output_dir_state)
        self.update_output_dir_state()
    
    def update_output_dir_state(self, *args):
        if self.output_mode_var.get() == "new_dir":
            for child in self.output_dir_frame.winfo_children():
                child.configure(state="normal")
        else:
            for child in self.output_dir_frame.winfo_children():
                if isinstance(child, ttk.Entry) or isinstance(child, ttk.Button):
                    child.configure(state="disabled")
    
    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("支持的文件", "*.py;*.js;*.html;*.htm;*.css"),
            ("Python文件", "*.py"),
            ("JavaScript文件", "*.js"),
            ("HTML文件", "*.html;*.htm"),
            ("CSS文件", "*.css"),
            ("所有文件", "*.*")
        ])
        if file_path:
            self.path_var.set(file_path)
    
    def select_directory(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.path_var.set(dir_path)
    
    def select_output_dir(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir_var.set(dir_path)
    
    def start_processing(self):
        path = self.path_var.get()
        if not path:
            messagebox.showerror("错误", "请选择文件或目录")
            return
        
        output_dir = None
        if self.output_mode_var.get() == "new_dir":
            output_dir = self.output_dir_var.get()
            if not output_dir:
                messagebox.showerror("错误", "请选择输出目录")
                return
        
        # 获取用户选择的文件类型
        file_types = []
        if self.py_var.get():
            file_types.append('py')
        if self.js_var.get():
            file_types.append('js')
        if self.html_var.get():
            file_types.append('html')
        if self.css_var.get():
            file_types.append('css')
        
        if not file_types:
            messagebox.showerror("错误", "请至少选择一种文件类型")
            return
        
        # 构建支持的文件扩展名字典
        supported_extensions = {}
        if 'py' in file_types:
            supported_extensions['.py'] = 'py'
        if 'js' in file_types:
            supported_extensions['.js'] = 'js'
        if 'html' in file_types:
            supported_extensions['.html'] = 'html'
            supported_extensions['.htm'] = 'html'
        if 'css' in file_types:
            supported_extensions['.css'] = 'css'
        
        self.status_var.set("处理中...")
        self.root.update()
        
        try:
            if os.path.isfile(path):
                # 获取文件扩展名
                _, ext = os.path.splitext(path)
                ext = ext.lower()
                
                # 检查是否支持该文件类型
                if ext not in supported_extensions:
                    messagebox.showwarning("警告", f"不支持的文件类型: {ext}")
                    self.status_var.set("准备就绪")
                    return
                
                success = process_file(path, output_dir, supported_extensions)
                if success:
                    messagebox.showinfo("成功", "文件处理完成")
                    self.status_var.set("处理完成")
                else:
                    messagebox.showerror("错误", "文件处理失败")
                    self.status_var.set("处理失败")
            else:  # 目录
                recursive = self.recursive_var.get()
                success_count, fail_count = process_directory(path, output_dir, recursive, file_types)
                
                if fail_count == 0:
                    messagebox.showinfo("成功", f"处理完成，成功处理 {success_count} 个文件")
                    self.status_var.set(f"处理完成，成功: {success_count}")
                else:
                    messagebox.showwarning("警告", f"处理完成，成功: {success_count}，失败: {fail_count}")
                    self.status_var.set(f"处理完成，成功: {success_count}，失败: {fail_count}")
        except Exception as e:
            messagebox.showerror("错误", f"处理过程中发生错误: {e}")
            self.status_var.set("处理失败")

    def setup_drop_target(self, widget):
        """配置拖放目标"""
        widget.drop_target_register(DND_FILES)
        widget.dnd_bind('<<Drop>>', self.handle_drop)
        widget.bind('<Enter>', lambda e: self.on_drag_enter(e, widget))
        widget.bind('<Leave>', lambda e: self.on_drag_leave(e, widget))

    def on_drag_enter(self, event, widget):
        """当拖动进入区域时改变视觉效果"""
        if isinstance(widget, ttk.Frame):
            widget.configure(style="DropZone.TFrame")
            self.drop_label.configure(foreground="blue")
        elif isinstance(widget, ttk.Entry):
            widget.state(['focus'])

    def on_drag_leave(self, event, widget):
        """当拖动离开区域时恢复视觉效果"""
        if isinstance(widget, ttk.Frame):
            widget.configure(style="TFrame")
            self.drop_label.configure(foreground="black")
        elif isinstance(widget, ttk.Entry):
            widget.state(['!focus'])

    def handle_drop(self, event):
        """处理拖放的文件或目录"""
        path = event.data
        # 移除可能的花括号（Windows特性）
        path = path.strip('{}')
        # 处理多个文件的情况，我们只取第一个
        if ' ' in path:
            path = path.split(' ')[0]
        
        self.path_var.set(path)
        if os.path.exists(path):
            if os.path.isfile(path):
                # 获取文件扩展名
                _, ext = os.path.splitext(path)
                ext = ext.lower()
                
                # 检查是否是支持的文件类型
                supported_extensions = ['.py', '.js', '.html', '.htm', '.css']
                if ext not in supported_extensions:
                    messagebox.showwarning("警告", f"不支持的文件类型: {ext}")
                else:
                    self.status_var.set("文件已添加，可以开始处理")
            else:
                self.status_var.set("目录已添加，可以开始处理")


def main():
    root = TkinterDnD.Tk()  # 使用TkinterDnD.Tk替代tk.Tk
    app = CommentRemoverApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()