"""表格视图组件 — Canvas + Label 网格，支持单格高亮"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.utils import col_letter


class TableView(tk.Frame):
    def __init__(self, parent, on_cell_click: callable):
        super().__init__(parent)
        self._on_cell_click = on_cell_click
        self._matrix: list[list] = []
        self._current_highlight: tuple[int, int] | None = None
        self._cell_widgets: dict[tuple[int, int], tk.Label] = {}

        # Canvas + 双滚动条
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.scroll_y = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._on_scroll_y)
        self.scroll_x = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self._on_scroll_x)

        # 内容框架 — 表头 + 数据都在里面
        self._content = tk.Frame(self.canvas, bg="white")
        self._header_frame: tk.Frame | None = None
        self._data_frame: tk.Frame | None = None
        self._canvas_win = self.canvas.create_window((0, 0), window=self._content, anchor="nw")

        # 布局
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scroll_y.grid(row=0, column=1, sticky="ns")
        self.scroll_x.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Canvas 绑定
        self._content.bind("<Configure>", self._on_content_resize)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self._bind_mousewheel()

    def _bind_mousewheel(self):
        self.canvas.bind("<Enter>", lambda e: self._arm_scroll())
        self.canvas.bind("<Leave>", lambda e: self._disarm_scroll())

    def _arm_scroll(self):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _disarm_scroll(self):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if event.num == 4 or (hasattr(event, "delta") and event.delta > 0):
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or (hasattr(event, "delta") and event.delta < 0):
            self.canvas.yview_scroll(1, "units")

    def _on_scroll_y(self, *args):
        self.canvas.yview(*args)

    def _on_scroll_x(self, *args):
        """水平滚动 — 同步表头和数据"""
        self.canvas.xview(*args)

    def _on_content_resize(self, event):
        """内容尺寸变化 → 更新可滚动区域 + 窗口宽度"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # 确保 canvas window 宽度 ≥ 内容实际宽度，水平滚动才能工作
        req_w = self._content.winfo_reqwidth()
        cur_w = self.canvas.winfo_width()
        if req_w > cur_w:
            self.canvas.itemconfigure(self._canvas_win, width=req_w)
        else:
            self.canvas.itemconfigure(self._canvas_win, width=cur_w)

    def _on_canvas_resize(self, event):
        """Canvas 大小变化 → 确保窗口宽度不低于视口"""
        req_w = self._content.winfo_reqwidth()
        if req_w < event.width:
            self.canvas.itemconfigure(self._canvas_win, width=event.width)

    def _column_letter(self, n: int) -> str:
        return col_letter(n)

    def refresh(self, matrix: list[list], handler):
        """重建表格"""
        self._matrix = matrix
        self._current_highlight = None
        self._cell_widgets.clear()

        # 清除旧内容
        for child in self._content.winfo_children():
            child.destroy()
        self._header_frame = None
        self._data_frame = None

        if not matrix:
            self.canvas.configure(scrollregion=(0, 0, 0, 0))
            return

        num_cols = len(matrix[0])
        if num_cols == 0:
            self.canvas.configure(scrollregion=(0, 0, 0, 0))
            return

        # ── 表头行 ──
        self._header_frame = tk.Frame(self._content, bg="#e8e8e8")
        self._header_frame.pack(fill=tk.X, side=tk.TOP)

        # 行号表头
        h = tk.Label(self._header_frame, text="行号", width=6,
                     bg="#e8e8e8", fg="#555", font=("", 9, "bold"),
                     relief=tk.GROOVE, borderwidth=1)
        h.pack(side=tk.LEFT)

        # 分隔线
        sep = tk.Label(self._header_frame, text="", width=1, bg="#d0d0d0")
        sep.pack(side=tk.LEFT)

        # 列标题
        for i in range(num_cols):
            letter = self._column_letter(i + 1)
            h = tk.Label(self._header_frame, text=letter, width=10,
                         bg="#e8e8e8", fg="#333", font=("", 9, "bold"),
                         relief=tk.GROOVE, borderwidth=1)
            h.pack(side=tk.LEFT)

        # ── 数据行 ──
        self._data_frame = tk.Frame(self._content, bg="white")
        self._data_frame.pack(fill=tk.BOTH, side=tk.TOP)

        for r_idx, row_data in enumerate(matrix):
            row_num = r_idx + 1
            row_frame = tk.Frame(self._data_frame, bg="white")
            row_frame.pack(fill=tk.X)

            # 行号
            rlbl = tk.Label(row_frame, text=str(row_num), width=6,
                            bg="#f5f5f5", fg="#888",
                            relief=tk.GROOVE, borderwidth=1,
                            font=("", 9))
            rlbl.pack(side=tk.LEFT)
            self._cell_widgets[(r_idx, 0)] = rlbl

            # 分隔线
            sep = tk.Label(row_frame, text="", width=1, bg="#e0e0e0", relief=tk.FLAT)
            sep.pack(side=tk.LEFT)

            # 数据单元格
            for c_idx, val in enumerate(row_data):
                text = str(val) if val is not None else ""
                display = text[:15] + "…" if len(text) > 16 else text

                lbl = tk.Label(row_frame, text=display, width=10,
                               bg="white", fg="#222",
                               relief=tk.GROOVE, borderwidth=1,
                               font=("", 9), anchor="center")
                lbl.pack(side=tk.LEFT)

                excel_col = c_idx + 1
                excel_row = row_num
                lbl.bind("<Button-1>",
                         lambda e, c=excel_col, r=excel_row: self._on_label_click(c, r))

                self._cell_widgets[(r_idx, c_idx + 1)] = lbl

        # 更新滚动区域
        self._content.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        req_w = self._content.winfo_reqwidth()
        canvas_w = self.canvas.winfo_width()
        self.canvas.itemconfigure(self._canvas_win, width=max(req_w, canvas_w))

    def _on_label_click(self, col: int, row: int):
        self.highlight(col, row)
        self._on_cell_click(col, row)

    def highlight(self, col: int, row: int):
        """高亮单个单元格"""
        if self._current_highlight:
            old_col, old_row = self._current_highlight
            old_key = (old_row - 1, old_col)
            if old_key in self._cell_widgets:
                self._cell_widgets[old_key].configure(
                    bg="white", relief=tk.GROOVE, borderwidth=1)

        key = (row - 1, col)
        if key in self._cell_widgets:
            self._cell_widgets[key].configure(
                bg="#cce5ff", relief=tk.SOLID, borderwidth=2)
            self._current_highlight = (col, row)

    def scroll_to(self, col: int, row: int):
        """滚动到指定行"""
        y_est = (row + 0.5) * 30
        total = max(1, len(self._matrix) * 30 + 30)
        self.canvas.yview_moveto(min(1, y_est / total))
