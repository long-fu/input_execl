"""录入模式导航逻辑"""
from __future__ import annotations

MODE_SINGLE = "single"
MODE_COL_INC = "col_inc"
MODE_ROW_INC = "row_inc"
MODE_FIXED_ROW = "fixed_row"

MODES = [MODE_SINGLE, MODE_COL_INC, MODE_ROW_INC, MODE_FIXED_ROW]

MODE_LABELS = {
    MODE_SINGLE: "逐格录入",
    MODE_COL_INC: "按列递增",
    MODE_ROW_INC: "按行递增",
    MODE_FIXED_ROW: "固定行",
}


class Navigator:
    """管理录入模式和光标位置"""

    def __init__(self):
        self.mode = MODE_SINGLE
        self.col = 1
        self.row = 1
        self.fixed_row = None

    def set_mode(self, mode: str):
        if mode not in MODES:
            raise ValueError(f"无效模式: {mode}")
        if mode == MODE_FIXED_ROW:
            self.fixed_row = self.row
        self.mode = mode

    def set_position(self, col: int, row: int):
        self.col = col
        self.row = row

    def reset(self):
        self.col = 1
        self.row = 1
        if self.mode == MODE_FIXED_ROW:
            self.fixed_row = 1

    def advance(self) -> tuple[int, int]:
        """返回下一个写入位置 (col, row)，并根据模式更新状态"""
        if self.mode == MODE_COL_INC:
            self.row += 1
        elif self.mode == MODE_ROW_INC:
            self.col += 1
        elif self.mode == MODE_FIXED_ROW:
            self.row = self.fixed_row
        # MODE_SINGLE 不自动推进
        return self.col, self.row
