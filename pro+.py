'''
Author: 择安网络
Date: 2025-03-15 18:07:14
LastEditTime: 2025-03-16 18:55:58
FilePath: /一键去注释/pro+.py
Code function: v1.1 保留头注释
'''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# 处理打包后的 tkinterdnd2 导入
def import_tkdnd():
    try:
        import tkinterdnd2
        return tkinterdnd2.DND_FILES, tkinterdnd2.TkinterDnD
    except ImportError:
        if getattr(sys, 'frozen', False):
            # 如果是打包后的环境
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            tkdnd_path = os.path.join(base_path, 'tkinterdnd2')
            if os.path.exists(tkdnd_path):
                sys.path.append(base_path)
                import tkinterdnd2
                return tkinterdnd2.DND_FILES, tkinterdnd2.TkinterDnD
        raise ImportError("Could not import tkinterdnd2")

# 获取 DND_FILES 和 TkinterDnD
DND_FILES, TkinterDnD = import_tkdnd()


def remove_comments_from_code(code, keep_header=False):
    """
    从Python代码中移除单行注释和多行注释，但保留文件头部注释
    
    Args:
        code (str): 原始Python代码
        keep_header (bool): 是否保留头部注释（包括标准Python头部注释和文件信息注释）
        
    Returns:
        str: 移除注释后的代码
    """

    header_comments = []
    if keep_header:
        lines = code.split('\n')
        i = 0
        while i < len(lines) and lines[i].strip().startswith('#'):
            line_stripped = lines[i].strip()
            if line_stripped.startswith('#!') or \
               line_stripped.startswith('# -*-') or \
               line_stripped.startswith('# coding=') or \
               line_stripped.startswith('# encoding='):
                header_comments.append(lines[i])
            i += 1
        
        remaining_code = '\n'.join(lines)
        file_info_pattern = r"'''[\s\S]*?Author:[\s\S]*?Code function:[\s\S]*?'''"
        file_info_match = re.search(file_info_pattern, remaining_code, re.MULTILINE)
        if file_info_match:
            if header_comments:
                header_comments.append('')
            header_comments.append(file_info_match.group(0))
    
    if keep_header and len(header_comments) > 0:
        code_parts = code.split(header_comments[-1], 1)
        if len(code_parts) > 1:
            code = code_parts[1]
    
    pattern = r'("""|\'\'\')[\s\S]*?\1'
    code = re.sub(pattern, '', code, flags=re.DOTALL)

    result = []
    lines = code.split('\n')
    in_string = False
    string_char = None
    
    for line in lines:
        new_line = ''
        i = 0
        while i < len(line):
            if not in_string and (line[i] == '"' or line[i] == "'"):
                in_string = True
                string_char = line[i]
                new_line += line[i]
            elif in_string and line[i] == string_char and (i == 0 or line[i-1] != '\\'):
                in_string = False
                new_line += line[i]
            elif not in_string and line[i] == '#':
                break
            else:
                new_line += line[i]
            i += 1
        
        if new_line.strip() or not line.lstrip().startswith('#'):
            result.append(new_line)
    
    if keep_header and header_comments:
        return '\n'.join(header_comments + [''] + [line for line in result if line.strip()])
    else:
        return '\n'.join([line for line in result if line.strip()])


def process_file(file_path, output_dir=None, keep_header=False):
    """
    处理单个Python文件，移除注释
    
    Args:
        file_path (str): 要处理的Python文件路径
        output_dir (str, optional): 输出目录，如果为None则覆盖原文件
        keep_header (bool): 是否保留头部注释
        
    Returns:
        bool: 处理是否成功
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        cleaned_code = remove_comments_from_code(code, keep_header)
        
        if output_dir:
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


def process_directory(dir_path, output_dir=None, recursive=True, keep_header=False):
    """
    处理目录中的所有Python文件
    
    Args:
        dir_path (str): 要处理的目录路径
        output_dir (str, optional): 输出目录
        recursive (bool): 是否递归处理子目录
        keep_header (bool): 是否保留头部注释
        
    Returns:
        tuple: (成功处理的文件数, 处理失败的文件数)
    """
    success_count = 0
    fail_count = 0
    
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                if output_dir:
                    rel_path = os.path.relpath(file_path, dir_path)
                    new_output_dir = os.path.join(output_dir, os.path.dirname(rel_path))
                    os.makedirs(new_output_dir, exist_ok=True)
                    output_path = os.path.join(output_dir, rel_path)
                else:
                    output_path = file_path
                
                if process_file(file_path, output_path if output_dir else None, keep_header):
                    success_count += 1
                else:
                    fail_count += 1
        
        if not recursive:
            break
    
    return success_count, fail_count


class CommentRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("交付壁垒(bz:择安网络)")
        self.root.geometry("600x521")
        
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#ccc")
        self.style.configure("TLabel", padding=6)
        self.style.configure("TCheckbutton", padding=6)
        self.style.configure("DropZone.TFrame", relief="solid", borderwidth=2)
        
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        select_frame = ttk.LabelFrame(main_frame, text="选择文件或目录", padding="10", style="DropZone.TFrame")
        select_frame.pack(fill=tk.X, pady=10)
        
        self.drop_label = ttk.Label(select_frame, text="拖放文件或文件夹到这里", font=("", 10, "italic"))
        self.drop_label.pack(pady=5)
        
        button_frame = ttk.Frame(select_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="选择文件", command=self.select_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="选择目录", command=self.select_directory).pack(side=tk.LEFT, padx=5)
        
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(button_frame, textvariable=self.path_var, width=50)
        self.path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.setup_drop_target(select_frame)
        self.setup_drop_target(self.path_entry)
        
        options_frame = ttk.LabelFrame(main_frame, text="选项", padding="10")
        options_frame.pack(fill=tk.X, pady=10)
        
        self.recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="递归处理子目录", variable=self.recursive_var).pack(anchor=tk.W)
        
        self.keep_header_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="保留Python头部注释", variable=self.keep_header_var).pack(anchor=tk.W)
        
        self.output_mode_var = tk.StringVar(value="overwrite")
        ttk.Radiobutton(options_frame, text="覆盖原文件", variable=self.output_mode_var, value="overwrite").pack(anchor=tk.W)
        ttk.Radiobutton(options_frame, text="输出到新目录", variable=self.output_mode_var, value="new_dir").pack(anchor=tk.W)
        
        self.output_dir_frame = ttk.Frame(options_frame)
        self.output_dir_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.output_dir_frame, text="输出目录:").pack(side=tk.LEFT)
        
        self.output_dir_var = tk.StringVar()
        ttk.Entry(self.output_dir_frame, textvariable=self.output_dir_var, width=40).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(self.output_dir_frame, text="浏览...", command=self.select_output_dir).pack(side=tk.LEFT, padx=5)
        
        status_frame = ttk.LabelFrame(main_frame, text="状态", padding="10")
        status_frame.pack(fill=tk.X, pady=10)
        
        self.status_var = tk.StringVar(value="准备就绪")
        ttk.Label(status_frame, textvariable=self.status_var).pack(anchor=tk.W)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="开始处理", command=self.start_processing).pack(side=tk.RIGHT, padx=5)
        
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
        file_path = filedialog.askopenfilename(filetypes=[("Python文件", "*.py"), ("所有文件", "*.*")])
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
        
        self.status_var.set("处理中...")
        self.root.update()
        
        try:
            if os.path.isfile(path):
                if not path.endswith('.py'):
                    messagebox.showwarning("警告", "选择的文件不是Python文件")
                    self.status_var.set("准备就绪")
                    return
                
                keep_header = self.keep_header_var.get()
                success = process_file(path, output_dir, keep_header)
                if success:
                    messagebox.showinfo("成功", "文件处理完成")
                    self.status_var.set("处理完成")
                else:
                    messagebox.showerror("错误", "文件处理失败")
                    self.status_var.set("处理失败")
            else:
                recursive = self.recursive_var.get()
                keep_header = self.keep_header_var.get()
                success_count, fail_count = process_directory(path, output_dir, recursive, keep_header)
                
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
        path = path.strip('{}')
        if ' ' in path:
            path = path.split(' ')[0]
        
        self.path_var.set(path)
        if os.path.exists(path):
            if os.path.isfile(path) and not path.endswith('.py'):
                messagebox.showwarning("警告", "选择的文件不是Python文件")
            else:
                self.status_var.set("文件已添加，可以开始处理")


def main():
    root = TkinterDnD.Tk()
    app = CommentRemoverApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()