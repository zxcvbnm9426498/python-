'''
Author: 择安网络
Date: 2025-03-15 19:58:34
LastEditTime: 2025-03-16 19:07:08
FilePath: /一键去注释/build.py
Code function: 
'''
import os
import sys
import subprocess
import tkinterdnd2

def get_tkdnd_path():
    return os.path.abspath(tkinterdnd2.__path__[0])

def main():
    tkdnd_path = get_tkdnd_path()
    
    # 构建 PyInstaller 命令
    if sys.platform == 'win32':
        separator = ';'
    else:
        separator = ':'
        
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        f'--add-data={tkdnd_path}{separator}tkinterdnd2',
        'pro+.py'
    ]
    
    print("Executing command:", ' '.join(cmd))
    subprocess.run(cmd)

if __name__ == '__main__':
    main() 