"""表格视图组件 — 基于 ttk.Treeview 展示 Excel 内容"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.utils import col_letter


class TableView(tk.Frame):
    def __init__(self, parent, on_cell_click: callable):
        super().__init__(parent)
        self._on_cell_click = on_cell_click
        self._current_highlight: tuple[int, int] | None = None

        # 滚动条
        self.v_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.h_scroll = ttk.Scrollbar(self, orient=tk.HORIZONTAL)

        # Treeview
        self.tree = ttk.Treeview(
            self,
            yscrollcommand=self.v_scroll.set,
            xscrollcommand=self.h_scroll.set,
            show="tree headings",
        )
        self.v_scroll.config(command=self.tree.yview)
        self.h_scroll.config(command=self.tree.xview)

        # 布局
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 绑定点击
        self.tree.bind("<ButtonRelease-1>", self._on_click)

    def _column_letter(self, n: int) -> str:
        """数字列号 → 字母列号（1→A, 27→AA）"""
        return col_letter(n)

    def refresh(self, matrix: list[list], handler):
        """完全重建表格"""
        # 清除旧数据
        self.tree.delete(*self.tree.get_children())
        cols = self.tree["columns"]
        self.tree["displaycolumns"] = ()

        if not matrix:
            return

        num_cols = len(matrix[0]) if matrix else 0
        if num_cols == 0:
            return

        # 设置列：col0 = 行号, col1..colN = A, B, C...
        self.tree["columns"] = [f"col_{i}" for i in range(num_cols)]

        # 行号列宽度根据最大行号动态计算
        max_row = len(matrix)
        row_header_width = max(50, len(str(max_row)) * 12 + 20)
        self.tree.column("#0", width=row_header_width, anchor="center")
        self.tree.heading("#0", text="")

        for i in range(num_cols):
            col_id = f"col_{i}"
            letter = self._column_letter(i + 1)
            self.tree.column(col_id, width=80, anchor="center", minwidth=60)
            self.tree.heading(col_id, text=letter)

        # 插入行
        for r_idx, row_data in enumerate(matrix):
            row_num = r_idx + 1
            values = [str(v) if v is not None else "" for v in row_data]
            self.tree.insert("", tk.END, iid=str(row_num), text=str(row_num), values=values)

    def _on_click(self, event):
        """点击单元格 → 解析行列 → 回调"""
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return

        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)

        if not row_id or not col_id:
            return

        row = int(row_id)
        col = int(col_id.lstrip("#"))  # col_id 是 "#N" 格式

        self._on_cell_click(col, row)

    def highlight(self, col: int, row: int):
        """高亮指定单元格"""
        # 清除旧高亮
        if self._current_highlight:
            old_col, old_row = self._current_highlight
            try:
                row_id = str(old_row)
                if self.tree.exists(row_id):
                    self.tree.tag_del(f"highlight_{old_row}_{old_col}")
            except Exception:
                pass

        # 设置新高亮
        try:
            row_id = str(row)
            tag = f"highlight_{row}_{col}"
            self.tree.tag_configure(tag, background="#cce5ff")
            self.tree.item(row_id, tags=(tag,))
            self._current_highlight = (col, row)
        except Exception:
            pass

    def scroll_to(self, col: int, row: int):
        """滚动到指定单元格可见"""
        try:
            row_id = str(row)
            if self.tree.exists(row_id):
                self.tree.see(row_id)
        except Exception:
            pass
