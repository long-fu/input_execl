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
        self._undo_stack: list[tuple[int, int, object]] = []  # (col, row, old_value)

        # 菜单
        self._build_menu()

        # 输入栏
        self.input_bar = InputBar(
            self.root,
            on_submit=self._on_submit,
            on_cell_change=self._on_cell_change,
            on_lock_toggle=self._on_lock_toggle,
            on_clear_row=self._on_clear_row,
            on_undo=self._undo,
        )
        self.input_bar.pack(fill=tk.X, padx=10, pady=(10, 2))

        # 表格 + 记录面板容器
        self._main_frame = tk.Frame(self.root)
        self._main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=2)
        self._main_frame.grid_rowconfigure(0, weight=1)
        self._main_frame.grid_columnconfigure(0, weight=1)

        # 表格视图（左侧）
        self.table_view = TableView(
            self._main_frame, on_cell_click=self._on_cell_click,
            font_family=self._font_name, font_size=self._font_size,
        )
        self.table_view.grid(row=0, column=0, sticky="nsew")
        self._refresh_table()

        # 输入记录面板（右侧，上方 60%）
        log_frame = tk.Frame(self._main_frame, width=180)
        log_frame.grid(row=0, column=1, sticky="ns", padx=(5, 0))
        log_frame.grid_propagate(False)
        log_frame.grid_rowconfigure(0, weight=6)  # 60%
        log_frame.grid_rowconfigure(1, weight=4)  # 40%
        log_frame.grid_columnconfigure(0, weight=1)

        # 输入记录（上方）
        log_top = tk.Frame(log_frame)
        log_top.grid(row=0, column=0, sticky="nsew")
        log_top.grid_rowconfigure(0, weight=1)
        log_top.grid_columnconfigure(0, weight=1)
        tk.Label(log_top, text="输入记录").pack()
        self._log_text = tk.Text(log_top, width=20, state=tk.DISABLED,
                                  font=(self._font_name, 10))
        log_scroll = tk.Scrollbar(log_top, command=self._log_text.yview)
        self._log_text.configure(yscrollcommand=log_scroll.set)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._log_text.pack(fill=tk.BOTH, expand=True)

        # 警戒列表（下方）
        alert_bottom = tk.Frame(log_frame)
        alert_bottom.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
        alert_bottom.grid_rowconfigure(0, weight=1)
        alert_bottom.grid_columnconfigure(0, weight=1)
        tk.Label(alert_bottom, text="警戒列表").pack()
        self._alert_text = tk.Text(alert_bottom, width=20, state=tk.DISABLED,
                                    fg="#cc0000", font=(self._font_name, 10))
        alert_scroll = tk.Scrollbar(alert_bottom, command=self._alert_text.yview)
        self._alert_text.configure(yscrollcommand=alert_scroll.set)
        alert_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._alert_text.pack(fill=tk.BOTH, expand=True)

        # 模式栏（已隐藏，默认固定行模式）
        self.mode_bar = ModeBar(self.root, on_mode_change=self._on_mode_change)
        # self.mode_bar.pack(fill=tk.X, padx=10, pady=2)

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

        self._update_row_sum()
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
        self.root.bind("<Escape>", lambda e: self.input_bar.clear_all())
        self.root.bind("<Control-z>", lambda e: self._undo())

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
        try:
            new_val = int(value)
        except (ValueError, TypeError):
            return  # 非整数不应到达（_handle_submit 已校验）

        overwritten = False
        existing = self.handler.read_cell(col, row)
        # 保存旧值到撤销栈
        self._undo_stack.append((col, row, existing))
        if existing != "":
            try:
                new_val += int(existing)
            except (ValueError, TypeError):
                overwritten = True  # 现有值非数字，被覆盖
        self.handler.write_cell(col, row, new_val)
        self.navigator.set_position(col, row)
        self._refresh_table()

        # 高亮刚写入的单元格
        self.table_view.highlight(col, row)
        self.table_view.scroll_to(col, row)

        # 根据模式推进位置
        _, next_row = self.navigator.advance()
        self.input_bar.clear_column()
        self.input_bar.set_row(next_row)
        self.input_bar.clear_value()
        self.input_bar.focus_column()

        self._update_row_sum()
        self._log_entry(str(col), row, value)
        msg = f"已写入 {col_letter(col)}{row} = {new_val}"
        if overwritten:
            msg += " (覆盖非数字原值)"
        self._update_status(msg)
        self._update_alert_list()

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
            self._update_row_sum()
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
        self._update_row_sum()
        self._update_status()
        self._update_alert_list()

    def _on_lock_toggle(self, locked: bool):
        """复选框切换固定行模式"""
        if locked:
            self._set_mode(MODE_FIXED_ROW)
        else:
            self._set_mode(MODE_SINGLE)
        self._update_row_sum()

    def _on_clear_row(self):
        """清空锁定行所有数据"""
        if self.navigator.mode != MODE_FIXED_ROW or not self.navigator.fixed_row:
            return
        r = self.navigator.fixed_row
        mc = self.handler.max_col
        for c in range(1, mc + 1):
            self.handler.write_cell(c, r, "")
        self._refresh_table()
        self._update_row_sum()
        self._update_status(f"已清空第 {r} 行")
        self._update_alert_list()

    def _undo(self):
        """撤销最近一次录入"""
        if not self._undo_stack:
            self._update_status("没有可撤销的操作")
            return
        col, row, old_val = self._undo_stack.pop()
        # 恢复旧值
        self.handler.write_cell(col, row, old_val if old_val != "" else "")
        self._refresh_table()
        self._update_row_sum()
        # 删除记录面板最后一行
        self._log_text.config(state=tk.NORMAL)
        last_start = self._log_text.index("end-2l linestart")
        self._log_text.delete(last_start, "end-1c")
        self._log_text.config(state=tk.DISABLED)
        old_display = old_val if old_val != "" else "(空)"
        self._update_status(f"已撤销 {col_letter(col)}{row}，恢复为 {old_display}")
        # 清空输入栏，光标回到列号
        self.input_bar.clear_column()
        self.input_bar.clear_value()
        self.input_bar.focus_column()
        self._update_alert_list()

    def _log_entry(self, col_label: str, row: int, value):
        """追加输入记录到右侧面板"""
        self._log_text.config(state=tk.NORMAL)
        self._log_text.insert(tk.END, f"{col_label};{row};{value}\n")
        self._log_text.see(tk.END)
        self._log_text.config(state=tk.DISABLED)

    def _update_row_sum(self):
        """更新锁定行的值合计"""
        if self.navigator.mode == MODE_FIXED_ROW and self.navigator.fixed_row:
            matrix = self.handler.get_matrix()
            r = self.navigator.fixed_row - 1  # matrix 索引从 0 开始
            if 0 <= r < len(matrix):
                total = 0
                for val in matrix[r]:
                    if val is not None and str(val).strip() != "":
                        try:
                            total += int(val)
                        except (ValueError, TypeError):
                            pass
                self.input_bar.set_row_sum(total)
                return
        self.input_bar.set_row_sum(0)

    def _compute_alert_cols(self) -> set[int]:
        """计算需要标红的列集合（仅在固定行模式下生效）"""
        if self.navigator.mode != MODE_FIXED_ROW or not self.navigator.fixed_row:
            return set()
        threshold = self.input_bar.get_alert_threshold()
        if threshold is None:
            return set()
        matrix = self.handler.get_matrix()
        r = self.navigator.fixed_row - 1
        if r < 0 or r >= len(matrix):
            return set()
        alert_cols = set()
        for c_idx, val in enumerate(matrix[r]):
            if val is not None and str(val).strip() != "":
                try:
                    if int(val) > threshold:
                        alert_cols.add(c_idx + 1)
                except (ValueError, TypeError):
                    pass
        return alert_cols

    def _update_alert_list(self):
        """更新右侧警戒列表：显示固定行中超过警戒值的单元格"""
        self._alert_text.config(state=tk.NORMAL)
        self._alert_text.delete("1.0", tk.END)

        if self.navigator.mode != MODE_FIXED_ROW or not self.navigator.fixed_row:
            self._alert_text.config(state=tk.DISABLED)
            return
        threshold = self.input_bar.get_alert_threshold()
        if threshold is None:
            self._alert_text.config(state=tk.DISABLED)
            return

        matrix = self.handler.get_matrix()
        r = self.navigator.fixed_row - 1
        if r < 0 or r >= len(matrix):
            self._alert_text.config(state=tk.DISABLED)
            return

        lines = []
        for c_idx, val in enumerate(matrix[r]):
            if val is not None and str(val).strip() != "":
                try:
                    if int(val) > threshold:
                        col_num = c_idx + 1
                        lines.append(f"{col_num} × {self.navigator.fixed_row} = {val}")
                except (ValueError, TypeError):
                    pass

        if lines:
            self._alert_text.insert(tk.END, "\n".join(lines))
        self._alert_text.config(state=tk.DISABLED)

    # ── 辅助方法 ──

    def _refresh_table(self):
        alert_cols = self._compute_alert_cols()
        self.table_view.refresh(self.handler.get_matrix(), self.handler, alert_cols)

    def _set_mode(self, mode: str):
        self.navigator.set_mode(mode)
        self.mode_bar.set_mode(mode)
        if mode == MODE_FIXED_ROW:
            self.input_bar.lock_row()
            self.input_bar.set_row(self.navigator.fixed_row)
        else:
            self.input_bar.unlock_row()
        self._update_status()
        self._update_alert_list()

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
