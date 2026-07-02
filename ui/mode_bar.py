"""模式切换栏 — 逐格/按列递增/按行递增"""
import tkinter as tk
from core.navigator import MODE_SINGLE, MODE_COL_INC, MODE_ROW_INC, MODE_FIXED_ROW, MODE_LABELS


class ModeBar(tk.Frame):
    def __init__(self, parent, on_mode_change: callable):
        super().__init__(parent)
        self._on_mode_change = on_mode_change
        self._var = tk.StringVar(value=MODE_SINGLE)

        tk.Label(self, text="模式:").pack(side=tk.LEFT, padx=(0, 10))

        for mode in [MODE_SINGLE, MODE_COL_INC, MODE_ROW_INC, MODE_FIXED_ROW]:
            rb = tk.Radiobutton(
                self, text=MODE_LABELS[mode], variable=self._var,
                value=mode, command=self._changed
            )
            rb.pack(side=tk.LEFT, padx=5)

    def _changed(self):
        self._on_mode_change(self._var.get())

    def set_mode(self, mode: str):
        self._var.set(mode)
