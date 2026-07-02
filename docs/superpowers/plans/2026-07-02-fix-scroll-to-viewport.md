# 修复 scroll_to 目标格不在窗口内

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 修复录入时目标单元格可能不在窗口可视范围内的问题。

**Architecture:** 单文件修复 — `table_view.py` 的 `scroll_to()` 方法中，`canvas.winfo_width()`/`winfo_height()` 可能返回过期值（如 1），导致滚动计算错误。在获取尺寸前调用 `update_idletasks()` 强制刷新布局。

**Tech Stack:** Python 3, tkinter

## 全局约束

- 不改变 scroll_to 的调用接口
- 不影响表头和行号列的固定行为

---

### Task 1: 修复 scroll_to 中 canvas 尺寸获取

**Files:**
- Modify: `ui/table_view.py:255-268`

**Interfaces:**
- Modifies: `TableView.scroll_to(col, row)` — 内部实现
- Produces: 无接口变更

- [ ] **Step 1: 在 scroll_to 中 winfo 调用前加 update_idletasks**

在 `scroll_to` 方法中，`cw = self.canvas.winfo_width()` 之前插入 `self.canvas.update_idletasks()`：

```python
    def scroll_to(self, col: int, row: int):
        if self._num_rows == 0:
            return
        self.canvas.update_idletasks()
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
```

- [ ] **Step 2: 验证**

启动应用，打开有数据的文件，确保：
- 输入列号/行号时，目标单元格自动滚动到可视范围内
- 点击表格单元格时，该格滚动到可视范围内
- 录入提交后，写入格滚动到可视范围内

- [ ] **Step 3: 提交**

```bash
git add ui/table_view.py
git commit -m "fix: scroll_to 调用 update_idletasks 确保 canvas 尺寸准确"
```
