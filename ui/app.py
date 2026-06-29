"""主窗口"""
from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path
from tkinter import filedialog, messagebox
from ui.input_bar import InputBar
from ui.table_view import TableView
from ui.mode_bar import ModeBar
from core.excel_handler import ExcelHandler
from core.navigator import Navigator, MODE_SINGLE, MODE_COL_INC, MODE_ROW_INC, MODE_FIXED_ROW, MODE_LABELS
from core.utils import col_letter

# 可用的中文字体优先级列表（Linux）
_FONT_CANDIDATES = [
    "Noto Sans CJK SC",
    "WenQuanYi Micro Hei",
    "WenQuanYi Zen Hei",
    "Noto Sans SC",
    "Source Han Sans SC",
    "DejaVu Sans",
    "sans-serif",
]

_FIXED_FONT_CANDIDATES = [
    "Noto Sans Mono CJK SC",
    "DejaVu Sans Mono",
    "monospace",
]


def _find_font(candidates: list[str], default: str = "TkDefaultFont") -> str:
    """从候选列表中找第一个系统可用的字体"""
    available = set(tkfont.families())
    for name in candidates:
        if name in available:
            return name
    return default


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Excel 快速录入工具")
        self.root.geometry("1000x650")
        self.root.minsize(600, 400)

        # ── 字体与 DPI 设置（解决 Linux 下模糊问题）──
        self._setup_fonts()

        self.handler = ExcelHandler()
        self.navigator = Navigator()

        # 菜单
        self._build_menu()

        # 输入栏
        self.input_bar = InputBar(
            self.root,
            on_submit=self._on_submit,
            on_cell_change=self._on_cell_change,
        )
        self.input_bar.pack(fill=tk.X, padx=10, pady=(10, 2))

        # 表格视图
        self.table_view = TableView(
            self.root, on_cell_click=self._on_cell_click,
            font_family=self._font_name, font_size=self._font_size,
        )
        self.table_view.pack(fill=tk.BOTH, expand=True, padx=10, pady=2)
        self._refresh_table()

        # 模式栏
        self.mode_bar = ModeBar(self.root, on_mode_change=self._on_mode_change)
        self.mode_bar.pack(fill=tk.X, padx=10, pady=2)

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(
            self.root, textvariable=self.status_var,
            anchor=tk.W, relief=tk.SUNKEN
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self._update_status()

        # 快捷键
        self._bind_shortcuts()

        self._update_title()

    def _setup_fonts(self):
        """配置清晰字体"""
        font_name = _find_font(_FONT_CANDIDATES)
        fixed_name = _find_font(_FIXED_FONT_CANDIDATES, font_name)
        self._font_name = font_name
        self._font_size = 11

        # 全局默认字体（显式 weight="normal" 避免粗细不均）
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(family=font_name, size=self._font_size, weight="normal")

        text_font = tkfont.nametofont("TkTextFont")
        text_font.configure(family=font_name, size=self._font_size, weight="normal")

        fixed_font = tkfont.nametofont("TkFixedFont")
        fixed_font.configure(family=fixed_name, size=self._font_size, weight="normal")

        # ttk 主题 — clam 渲染更清晰
        try:
            self.root.tk.call("ttk::style", "theme", "use", "clam")
        except Exception:
            pass

    # ── 菜单 ──

    def _build_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="新建 (Ctrl+N)", command=self._file_new)
        file_menu.add_command(label="打开 (Ctrl+O)", command=self._file_open)
        file_menu.add_command(label="保存 (Ctrl+S)", command=self._file_save)
        file_menu.add_command(label="另存为...", command=self._file_save_as)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)

        # 编辑菜单（占位）
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self._show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)

    def _show_about(self):
        messagebox.showinfo("关于", "Excel 快速录入工具 v1.0")

    # ── 快捷键 ──

    def _bind_shortcuts(self):
        self.root.bind("<Control-o>", lambda e: self._file_open())
        self.root.bind("<Control-s>", lambda e: self._file_save())
        self.root.bind("<Control-n>", lambda e: self._file_new())
        self.root.bind("<Control-Key-1>", lambda e: self._set_mode(MODE_SINGLE))
        self.root.bind("<Control-Key-2>", lambda e: self._set_mode(MODE_COL_INC))
        self.root.bind("<Control-Key-3>", lambda e: self._set_mode(MODE_ROW_INC))
        self.root.bind("<Control-Key-4>", lambda e: self._set_mode(MODE_FIXED_ROW))
        self.root.bind("<Escape>", lambda e: self.input_bar.clear_all())

    # ── 文件操作 ──

    def _file_new(self):
        if self.handler.filepath is None:
            if not messagebox.askyesno("未保存更改", "当前文件尚未保存，确定放弃吗？"):
                return
        self.handler.new()
        self.navigator.reset()
        self.input_bar.clear_all()
        self.input_bar.set_column(1)
        self.input_bar.set_row(1)
        self._refresh_table()
        self._update_title()
        self._update_status()

    def _file_open(self):
        if self.handler.filepath is None:
            if not messagebox.askyesno("未保存更改", "当前文件尚未保存，确定放弃吗？"):
                return
        path = filedialog.askopenfilename(
            filetypes=[("Excel 文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        if not path:
            return
        try:
            self.handler = ExcelHandler(path)
            self.navigator.reset()
            self.input_bar.clear_all()
            self.input_bar.set_column(1)
            self.input_bar.set_row(1)
            self._refresh_table()
            self._update_title()
            self._update_status()
        except Exception as e:
            messagebox.showerror("打开失败", str(e))

    def _file_save(self):
        try:
            if self.handler.filepath:
                self.handler.save()
                self._update_status("已保存")
            else:
                self._file_save_as()
        except Exception as e:
            messagebox.showerror("保存失败", str(e))

    def _file_save_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel 文件", "*.xlsx"), ("所有文件", "*.*")]
        )
        if not path:
            return
        try:
            self.handler.save_as(path)
            self._update_title()
            self._update_status("已保存")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))

    # ── 录入回调 ──

    def _on_submit(self, col: int, row: int, value: str):
        new_val = float(value)
        existing = self.handler.read_cell(col, row)
        if existing != "":
            try:
                new_val += float(existing)
            except ValueError:
                pass  # 现有值非数字则覆盖
        self.handler.write_cell(col, row, new_val)
        self.navigator.set_position(col, row)
        self._refresh_table()

        # 高亮刚写入的单元格
        self.table_view.highlight(col, row)
        self.table_view.scroll_to(col, row)

        # 根据模式推进位置
        next_col, next_row = self.navigator.advance()
        self.input_bar.set_column(next_col)
        self.input_bar.set_row(next_row)
        self.input_bar.clear_value()
        self.input_bar.focus_value()

        self._update_status(f"已写入 {col_letter(col)}{row} = {new_val}")

    def _on_cell_change(self, col: int, row: int):
        """输入栏列号/行号变化时高亮对应单元格"""
        self.navigator.set_position(col, row)
        self.table_view.highlight(col, row)
        self.table_view.scroll_to(col, row)

    def _on_cell_click(self, col: int, row: int):
        """表格单元格被点击 → 填充输入栏"""
        self.input_bar.set_column(col)
        if self.navigator.mode == MODE_FIXED_ROW:
            # 固定行模式：点击单元格更新固定行目标
            self.navigator.fixed_row = row
            self.navigator.set_position(col, row)
            self.input_bar.set_row(row)
            current_value = self.handler.read_cell(col, row)
            self.input_bar.set_value(current_value)
            self.table_view.highlight(col, row)
            self.table_view.scroll_to(col, row)
        else:
            self.navigator.set_position(col, row)
            self.input_bar.set_row(row)
            current_value = self.handler.read_cell(col, row)
            self.input_bar.set_value(current_value)
            self.table_view.highlight(col, row)
            self.table_view.scroll_to(col, row)
        self.input_bar.focus_value()

    def _on_mode_change(self, mode: str):
        self.navigator.set_mode(mode)
        if mode == MODE_FIXED_ROW:
            self.input_bar.lock_row()
            self.input_bar.set_row(self.navigator.fixed_row)
        else:
            self.input_bar.unlock_row()
        self._update_status()

    # ── 辅助方法 ──

    def _refresh_table(self):
        self.table_view.refresh(self.handler.get_matrix(), self.handler)

    def _set_mode(self, mode: str):
        self.navigator.set_mode(mode)
        self.mode_bar.set_mode(mode)
        if mode == MODE_FIXED_ROW:
            self.input_bar.lock_row()
            self.input_bar.set_row(self.navigator.fixed_row)
        else:
            self.input_bar.unlock_row()
        self._update_status()

    def _update_title(self):
        fp = self.handler.filepath
        name = Path(fp).name if fp else "未命名"
        self.root.title(f"Excel 快速录入工具 — {name}")

    def _update_status(self, msg: str | None = None):
        fp = self.handler.filepath
        name = Path(fp).name if fp else "未命名"
        saved = "已保存" if fp else "未保存"
        pos = f"{col_letter(self.navigator.col)}{self.navigator.row}"
        mode_label = MODE_LABELS.get(self.navigator.mode, self.navigator.mode)
        self.status_var.set(
            f"  {name} | {saved} | 位置: {pos} | 模式: {mode_label}"
            + (f" | {msg}" if msg else "")
        )
