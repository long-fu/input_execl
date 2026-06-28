"""表格视图组件 — Canvas + Label 网格，支持单格高亮"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.utils import col_letter

CELL_W = 80    # 数据列宽
CELL_H = 28    # 行高
ROW_NO_W = 50  # 行号列宽
HEADER_H = 26  # 表头高


class TableView(tk.Frame):
    def __init__(self, parent, on_cell_click: callable):
        super().__init__(parent)
        self._on_cell_click = on_cell_click
        self._matrix: list[list] = []
        self._current_highlight: tuple[int, int] | None = None
        self._cell_widgets: dict[tuple[int, int], tk.Label] = {}
        self._header_widgets: list[tk.Label] = []

        # 顶部固定表头
        self._header_frame = tk.Frame(self, bg="#e8e8e8")
        self._header_frame.pack(fill=tk.X, side=tk.TOP)

        # Canvas + 滚动
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.scroll_y = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scroll_x = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        self._grid_frame = tk.Frame(self.canvas, bg="white")
        self._canvas_win = self.canvas.create_window((0, 0), window=self._grid_frame, anchor="nw")

        self.canvas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.scroll_y.pack(fill=tk.Y, side=tk.RIGHT)
        self.scroll_x.pack(fill=tk.X, side=tk.BOTTOM)

        # 滚动事件
        self._grid_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _column_letter(self, n: int) -> str:
        return col_letter(n)

    def refresh(self, matrix: list[list], handler):
        """重建表格"""
        self._matrix = matrix
        self._current_highlight = None

        # 清除旧控件
        for w in self._header_widgets:
            w.destroy()
        self._header_widgets.clear()
        for w in self._cell_widgets.values():
            w.destroy()
        self._cell_widgets.clear()
        for child in self._grid_frame.winfo_children():
            child.destroy()

        if not matrix:
            return

        num_cols = len(matrix[0])
        if num_cols == 0:
            return

        # ── 表头 ──
        # 行号表头
        h = tk.Label(self._header_frame, text="行号", width=6,
                     bg="#e8e8e8", fg="#555", font=("", 9, "bold"),
                     relief=tk.GROOVE, borderwidth=1)
        h.pack(side=tk.LEFT)
        self._header_widgets.append(h)

        # 分隔线
        sep = tk.Label(self._header_frame, text="", width=1, bg="#d0d0d0")
        sep.pack(side=tk.LEFT)
        self._header_widgets.append(sep)

        # 列标题
        for i in range(num_cols):
            letter = self._column_letter(i + 1)
            h = tk.Label(self._header_frame, text=letter, width=10,
                         bg="#e8e8e8", fg="#333", font=("", 9, "bold"),
                         relief=tk.GROOVE, borderwidth=1)
            h.pack(side=tk.LEFT)
            self._header_widgets.append(h)

        # ── 数据行 ──
        for r_idx, row_data in enumerate(matrix):
            row_num = r_idx + 1
            row_frame = tk.Frame(self._grid_frame, bg="white")
            row_frame.pack(fill=tk.X)

            # 行号
            rlbl = tk.Label(row_frame, text=str(row_num), width=6,
                            bg="#f5f5f5", fg="#888",
                            relief=tk.GROOVE, borderwidth=1,
                            font=("", 9))
            rlbl.pack(side=tk.LEFT)
            self._cell_widgets[(r_idx, 0)] = rlbl  # col=0 表示行号

            # 分隔线
            sep = tk.Label(row_frame, text="", width=1, bg="#e0e0e0", relief=tk.FLAT)
            sep.pack(side=tk.LEFT)
            self._cell_widgets[(r_idx, -1)] = sep

            # 数据单元格
            for c_idx, val in enumerate(row_data):
                text = str(val) if val is not None else ""
                # 截断过长文本
                display = text[:15] + "…" if len(text) > 16 else text

                lbl = tk.Label(row_frame, text=display, width=10,
                               bg="white", fg="#222",
                               relief=tk.GROOVE, borderwidth=1,
                               font=("", 9),
                               anchor="center")
                lbl.pack(side=tk.LEFT)

                # 绑定点击
                excel_col = c_idx + 1
                excel_row = row_num
                lbl.bind("<Button-1>",
                         lambda e, c=excel_col, r=excel_row: self._on_label_click(c, r))

                self._cell_widgets[(r_idx, c_idx + 1)] = lbl

    def _on_label_click(self, col: int, row: int):
        """单元格被点击"""
        self.highlight(col, row)
        self._on_cell_click(col, row)

    def highlight(self, col: int, row: int):
        """高亮单个单元格 — 深色边框 + 浅蓝底色"""
        # 还原旧高亮
        if self._current_highlight:
            old_col, old_row = self._current_highlight
            old_key = (old_row - 1, old_col)
            if old_key in self._cell_widgets:
                lbl = self._cell_widgets[old_key]
                lbl.configure(bg="white", relief=tk.GROOVE, borderwidth=1)

        # 设置新高亮
        key = (row - 1, col)
        if key in self._cell_widgets:
            lbl = self._cell_widgets[key]
            lbl.configure(bg="#cce5ff", relief=tk.SOLID, borderwidth=2)
            self._current_highlight = (col, row)

    def scroll_to(self, col: int, row: int):
        """滚动到指定行"""
        # 估算 y 位置
        y = (row - 1) * (CELL_H + 2)  # 2px pack spacing
        total_h = len(self._matrix) * (CELL_H + 2)
        if total_h > 0:
            fraction = max(0, min(1, y / total_h))
            self.canvas.yview_moveto(fraction)
