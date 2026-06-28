"""表格视图组件 — Canvas 绘制，表头悬浮 + 行号列固定"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.utils import col_letter

ROW_NO_W = 60
COL_W = 80
SEP_W = 7
ROW_H = 26
HEADER_H = 26


class TableView(tk.Frame):
    def __init__(self, parent, on_cell_click: callable,
                 font_family: str = "", font_size: int = 11):
        super().__init__(parent)
        self._on_cell_click = on_cell_click
        self._matrix: list[list] = []
        self._num_cols = 0
        self._num_rows = 0
        self._current_highlight: tuple[int, int] | None = None

        family = font_family if font_family else "TkDefaultFont"
        self._font = (family, font_size, "normal")
        self._font_bold = (family, font_size, "bold")

        # Canvas
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.scroll_y = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._on_yscroll)
        self.scroll_x = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self._on_xscroll)
        self.canvas.configure(yscrollcommand=self.scroll_y.set,
                              xscrollcommand=self.scroll_x.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scroll_y.grid(row=0, column=1, sticky="ns")
        self.scroll_x.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas.bind("<Button-1>", self._on_click)
        self._bind_mousewheel()

    # ── 鼠标滚轮 ──

    def _bind_mousewheel(self):
        self.canvas.bind("<Enter>", lambda e: self._arm())
        self.canvas.bind("<Leave>", lambda e: self._disarm())

    def _arm(self):
        self.canvas.bind_all("<MouseWheel>", self._on_mwheel)
        self.canvas.bind_all("<Button-4>", self._on_mwheel)
        self.canvas.bind_all("<Button-5>", self._on_mwheel)

    def _disarm(self):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mwheel(self, event):
        if event.num == 4 or (hasattr(event, "delta") and event.delta > 0):
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or (hasattr(event, "delta") and event.delta < 0):
            self.canvas.yview_scroll(1, "units")
        self._pin()

    # ── 滚动 + 固定 ──

    def _on_yscroll(self, *args):
        self.canvas.yview(*args)
        self._pin()

    def _on_xscroll(self, *args):
        self.canvas.xview(*args)
        self._pin()

    def _pin(self):
        """固定表头在顶部，行号列在左侧"""
        view_top = self.canvas.canvasy(0)
        view_left = self.canvas.canvasx(0)

        # 顶部固定：header 项目（含行号表头、分隔表头、列字母表头）
        for item in self.canvas.find_withtag("pin_top"):
            coords = self.canvas.coords(item)
            if len(coords) == 4:
                h = coords[3] - coords[1]
                self.canvas.coords(item, coords[0], view_top, coords[2], view_top + h)
            elif len(coords) == 2:
                self.canvas.coords(item, coords[0], view_top + HEADER_H / 2)

        # 左侧固定：行号 + 分隔线
        for item in self.canvas.find_withtag("pin_left"):
            coords = self.canvas.coords(item)
            if len(coords) == 4:
                w = coords[2] - coords[0]
                self.canvas.coords(item, view_left, coords[1], view_left + w, coords[3])
            elif len(coords) == 2:
                self.canvas.coords(item, view_left + ROW_NO_W / 2, coords[1])

        self.canvas.tag_raise("pin_top")
        self.canvas.tag_raise("pin_left")

    # ── 坐标 ──

    def _col_x(self, col: int) -> int:
        return ROW_NO_W + SEP_W + (col - 1) * COL_W

    def _row_y(self, row: int) -> int:
        return HEADER_H + (row - 1) * ROW_H

    def _total_w(self) -> int:
        return ROW_NO_W + SEP_W + self._num_cols * COL_W

    def _total_h(self) -> int:
        return HEADER_H + self._num_rows * ROW_H

    # ── 绘制 ──

    def refresh(self, matrix: list[list], handler):
        self._matrix = matrix
        self._current_highlight = None
        self.canvas.delete("all")

        if not matrix:
            self.canvas.configure(scrollregion=(0, 0, 0, 0))
            return

        self._num_cols = len(matrix[0])
        self._num_rows = len(matrix)
        if self._num_cols == 0:
            self.canvas.configure(scrollregion=(0, 0, 0, 0))
            return

        tw = self._total_w()
        th = self._total_h()
        self.canvas.configure(scrollregion=(0, 0, tw, th))

        # ── 表头 ──
        # 行号表头 — pin_top + pin_left
        self.canvas.create_rectangle(0, 0, ROW_NO_W, HEADER_H,
                                     fill="#e8e8e8", outline="#c0c0c0",
                                     tags=("pin_top", "pin_left"))
        self.canvas.create_text(ROW_NO_W // 2, HEADER_H // 2,
                                text="行号", fill="#555", font=self._font_bold,
                                tags=("pin_top", "pin_left"))
        # 分隔表头
        self.canvas.create_rectangle(ROW_NO_W, 0, ROW_NO_W + SEP_W, HEADER_H,
                                     fill="#d0d0d0", outline="#c0c0c0",
                                     tags=("pin_top", "pin_left"))
        # 列表头 — pin_top only
        for ci in range(1, self._num_cols + 1):
            x = self._col_x(ci)
            self.canvas.create_rectangle(x, 0, x + COL_W, HEADER_H,
                                         fill="#e8e8e8", outline="#c0c0c0",
                                         tags=("pin_top",))
            self.canvas.create_text(x + COL_W // 2, HEADER_H // 2,
                                    text=col_letter(ci), fill="#333",
                                    font=self._font_bold, tags=("pin_top",))

        # ── 行号列 — pin_left ──
        for r in range(1, self._num_rows + 1):
            y = self._row_y(r)
            self.canvas.create_rectangle(0, y, ROW_NO_W, y + ROW_H,
                                         fill="#f5f5f5", outline="#e0e0e0",
                                         tags=("pin_left",))
            self.canvas.create_text(ROW_NO_W // 2, y + ROW_H // 2,
                                    text=str(r), fill="#888", font=self._font,
                                    tags=("pin_left",))

        # ── 分隔线 — pin_left ──
        for r in range(1, self._num_rows + 1):
            y = self._row_y(r)
            self.canvas.create_rectangle(ROW_NO_W, y, ROW_NO_W + SEP_W, y + ROW_H,
                                         fill="#e0e0e0", outline="",
                                         tags=("pin_left",))

        # ── 数据单元格 ──
        for r_idx, row_data in enumerate(matrix):
            r = r_idx + 1
            y = self._row_y(r)
            for c_idx, val in enumerate(row_data):
                c = c_idx + 1
                x = self._col_x(c)
                text = str(val) if val is not None else ""
                display = text[:16] + "…" if len(text) > 17 else text

                tag = f"cell_{r}_{c}"
                self.canvas.create_rectangle(x, y, x + COL_W, y + ROW_H,
                                             fill="white", outline="#e0e0e0",
                                             tags=("cell", tag))
                self.canvas.create_text(x + COL_W // 2, y + ROW_H // 2,
                                        text=display, fill="#222", font=self._font,
                                        tags=("cell", tag))

        self._pin()

    # ── 点击 ──

    def _on_click(self, event):
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)

        if cy < HEADER_H:
            return
        if cx < ROW_NO_W + SEP_W:
            return

        col = int((cx - ROW_NO_W - SEP_W) // COL_W) + 1
        row = int((cy - HEADER_H) // ROW_H) + 1

        if col < 1 or col > self._num_cols:
            return
        if row < 1 or row > self._num_rows:
            return

        self.highlight(col, row)
        self._on_cell_click(col, row)

    # ── 高亮 ──

    def highlight(self, col: int, row: int):
        if self._current_highlight:
            oc, o_r = self._current_highlight
            self._draw_cell_bg(oc, o_r, fill="white", outline="#e0e0e0")
        self._draw_cell_bg(col, row, fill="#cce5ff", outline="#4a90d9")
        self.canvas.tag_raise("pin_top")
        self.canvas.tag_raise("pin_left")
        self._current_highlight = (col, row)

    def _draw_cell_bg(self, col: int, row: int, fill: str, outline: str):
        if row < 1 or row > self._num_rows or col < 1 or col > self._num_cols:
            return
        tag = f"cell_{row}_{col}"
        x = self._col_x(col)
        y = self._row_y(row)
        items = self.canvas.find_withtag(tag)
        for item in items:
            if self.canvas.type(item) == "rectangle":
                self.canvas.delete(item)
        rect_id = self.canvas.create_rectangle(x, y, x + COL_W, y + ROW_H,
                                               fill=fill, outline=outline,
                                               tags=("cell", tag))
        self.canvas.tag_lower(rect_id)

    def scroll_to(self, col: int, row: int):
        if self._num_rows == 0:
            return
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        th = self._total_h()
        if th > ch > 0:
            y = self._row_y(row) - ch // 2
            self.canvas.yview_moveto(max(0, min(1, y / (th - ch))))
        tw = self._total_w()
        if tw > cw > 0:
            x = self._col_x(col) - cw // 2
            self.canvas.xview_moveto(max(0, min(1, x / (tw - cw))))
        self._pin()
