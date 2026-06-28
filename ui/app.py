"""主窗口"""
import tkinter as tk
from ui.input_bar import InputBar
from core.excel_handler import ExcelHandler
from core.navigator import Navigator


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Excel 快速录入工具")
        self.root.geometry("900x600")

        self.handler = ExcelHandler()
        self.navigator = Navigator()

        # 输入栏
        self.input_bar = InputBar(
            self.root,
            on_submit=self._on_submit,
            on_cell_change=self._on_cell_change,
        )
        self.input_bar.pack(fill=tk.X, padx=10, pady=(10, 5))

        self._update_title()

    def _on_submit(self, col: int, row: int, value: str):
        self.handler.write_cell(col, row, value)
        self.navigator.set_position(col, row)
        # 根据模式推进位置
        next_col, next_row = self.navigator.advance()
        self.input_bar.set_column(next_col)
        self.input_bar.set_row(next_row)
        self.input_bar.clear_value()
        self.input_bar.focus_value()

    def _on_cell_change(self, col: int, row: int):
        pass  # 后续 task 中连接 table_view 高亮

    def _update_title(self):
        fp = self.handler.filepath
        name = fp if fp else "未命名"
        self.root.title(f"Excel 快速录入工具 — {name}")
