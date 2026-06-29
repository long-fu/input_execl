"""输入栏组件 — 列号、行号、数值输入框 + 录入按钮"""
from __future__ import annotations

import tkinter as tk


class InputBar(tk.Frame):
    def __init__(self, parent, on_submit: callable, on_cell_change: callable | None = None,
                 on_lock_toggle: callable | None = None):
        super().__init__(parent)
        self._on_submit = on_submit
        self._on_cell_change = on_cell_change
        self._on_lock_toggle = on_lock_toggle

        # 列号
        tk.Label(self, text="列号:").pack(side=tk.LEFT, padx=(0, 2))
        self.col_entry = tk.Entry(self, width=8)
        self.col_entry.pack(side=tk.LEFT, padx=(0, 10))

        # 行号
        tk.Label(self, text="行号:").pack(side=tk.LEFT, padx=(0, 2))
        self.row_entry = tk.Entry(self, width=8)
        self.row_entry.pack(side=tk.LEFT, padx=(0, 10))

        # 数值
        tk.Label(self, text="数值:").pack(side=tk.LEFT, padx=(0, 2))
        self.value_entry = tk.Entry(self, width=24)
        self.value_entry.pack(side=tk.LEFT, padx=(0, 10))

        # 录入按钮
        self.submit_btn = tk.Button(self, text="录入", command=self._handle_submit, width=8)
        self.submit_btn.pack(side=tk.LEFT)

        # 锁定行号复选框
        self._lock_var = tk.BooleanVar(value=False)
        self.lock_cb = tk.Checkbutton(
            self, text="锁定行号", variable=self._lock_var,
            command=self._on_lock_changed
        )
        self.lock_cb.pack(side=tk.LEFT, padx=(10, 0))

        # 绑定键盘事件
        self.col_entry.bind("<Return>", self._on_col_return)
        self.row_entry.bind("<Return>", lambda e: self.value_entry.focus_set())
        self.value_entry.bind("<Return>", lambda e: self._handle_submit())
        self.col_entry.bind("<Tab>", self._on_tab)
        self.row_entry.bind("<Tab>", self._on_tab)
        self.value_entry.bind("<Tab>", self._on_tab)

        # 列号/行号变化时通知 table_view 高亮
        self.col_entry.bind("<KeyRelease>", self._notify_cell_change)
        self.row_entry.bind("<KeyRelease>", self._notify_cell_change)


    def _on_col_return(self, event=None):
        """列号回车 → 行号或数值，锁定行时跳过行号"""
        if self.row_entry.cget("state") == "readonly":
            self.value_entry.focus_set()
        else:
            self.row_entry.focus_set()

    def _on_tab(self, event):
        """Tab 切换到下一个输入框，锁定行时跳过行号"""
        current = event.widget
        row_locked = self.row_entry.cget("state") == "readonly"
        if current == self.col_entry:
            if row_locked:
                self.value_entry.focus_set()
            else:
                self.row_entry.focus_set()
        elif current == self.row_entry:
            self.value_entry.focus_set()
        elif current == self.value_entry:
            self.col_entry.focus_set()
        return "break"

    def _notify_cell_change(self, event=None):
        if self._on_cell_change:
            col = self._parse_col()
            row = self._parse_int(self.row_entry.get())
            if col is not None and row is not None:
                self._on_cell_change(col, row)

    def _parse_col(self) -> int | None:
        """解析列号：支持字母(A=1, Z=26, AA=27)和数字"""
        text = self.col_entry.get().strip().upper()
        if not text:
            return None
        # 尝试数字
        try:
            n = int(text)
            if n >= 1:
                return n
        except ValueError:
            pass
        # 尝试字母
        try:
            col_num = 0
            for ch in text:
                if "A" <= ch <= "Z":
                    col_num = col_num * 26 + (ord(ch) - ord("A") + 1)
                else:
                    return None
            return col_num if col_num >= 1 else None
        except Exception:
            return None

    @staticmethod
    def _parse_int(text: str) -> int | None:
        try:
            n = int(text.strip())
            return n if n >= 1 else None
        except ValueError:
            return None

    def _handle_submit(self):
        col = self._parse_col()
        row = self._parse_int(self.row_entry.get())
        value = self.value_entry.get()

        if col is None:
            self.col_entry.config(bg="#ffe0e0")
            return
        if row is None:
            self.row_entry.config(bg="#ffe0e0")
            return

        # 校验数值：必须为数字
        if not value.strip():
            self.value_entry.config(bg="#ffe0e0")
            return
        try:
            float(value)
        except ValueError:
            self.value_entry.config(bg="#ffe0e0")
            return

        # 恢复正常背景（锁定行不恢复）
        self.col_entry.config(bg="white")
        if self.row_entry.cget("state") != "readonly":
            self.row_entry.config(bg="white")
        self.value_entry.config(bg="white")

        self._on_submit(col, row, value)

    def set_column(self, col: int):
        self.col_entry.delete(0, tk.END)
        self.col_entry.insert(0, str(col))

    def set_row(self, row: int):
        self.row_entry.delete(0, tk.END)
        self.row_entry.insert(0, str(row))

    def _on_lock_changed(self):
        """复选框切换锁定状态"""
        if self._on_lock_toggle:
            self._on_lock_toggle(self._lock_var.get())

    def lock_row(self):
        """锁定行号输入框（固定行模式）"""
        self._lock_var.set(True)
        self.row_entry.config(state="readonly", bg="#d9d9d9", fg="#666666")

    def unlock_row(self):
        """解锁行号输入框"""
        self._lock_var.set(False)
        self.row_entry.config(state="normal", bg="white", fg="black")

    def set_value(self, val):
        self.value_entry.delete(0, tk.END)
        self.value_entry.insert(0, str(val) if val is not None else "")

    def focus_value(self):
        self.value_entry.focus_set()

    def focus_column(self):
        self.col_entry.focus_set()

    def clear_value(self):
        self.value_entry.delete(0, tk.END)

    def clear_all(self):
        self.col_entry.delete(0, tk.END)
        self.row_entry.delete(0, tk.END)
        self.value_entry.delete(0, tk.END)
