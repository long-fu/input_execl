"""主窗口"""
import tkinter as tk


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Excel 快速录入工具")
        self.root.geometry("900x600")

        # 临时占位标签，后续任务会替换
        label = tk.Label(root, text="Excel 快速录入工具", font=("", 20))
        label.pack(pady=50)
