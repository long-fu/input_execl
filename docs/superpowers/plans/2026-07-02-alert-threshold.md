# 警戒值功能实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在输入栏增加警戒值输入框，固定行模式下锁定行中某列值超过警戒值时，整列标红。

**Architecture:** 三层改动——InputBar 新增警戒值 Entry 和 getter、TableView.refresh() 接受 alert_cols 集合控制列样式、App 新增 _compute_alert_cols() 连接两者。

**Tech Stack:** Python 3, tkinter

## 全局约束

- 仅在固定行模式（MODE_FIXED_ROW）下生效
- 警戒值为空时视为不启用
- 标红范围：该列所有行（含表头）
- 颜色：背景 `#ffe0e0`，文字 `#cc0000`，边框 `#e0a0a0`

---

### Task 1: InputBar 新增警戒值输入框

**Files:**
- Modify: `ui/input_bar.py`

**Interfaces:**
- Produces: `InputBar.alert_entry: tk.Entry`，`InputBar.get_alert_threshold() -> int | None`

- [ ] **Step 1: 在 `__init__` 中新增警戒值 Label 和 Entry**

在 `_sum_label.pack(...)` 之后、数值 Label 之前插入：

```python
        # 警戒值
        tk.Label(self, text="警戒值:").pack(side=tk.LEFT, padx=(0, 2))
        self.alert_entry = tk.Entry(self, width=6)
        self.alert_entry.pack(side=tk.LEFT, padx=(0, 10))
```

- [ ] **Step 2: 新增 `get_alert_threshold()` 方法**

在 `_parse_int` 静态方法之后新增：

```python
    def get_alert_threshold(self) -> int | None:
        """返回警戒值，为空或非整数时返回 None"""
        text = self.alert_entry.get().strip()
        if not text:
            return None
        try:
            n = int(text)
            return n if n >= 0 else None
        except ValueError:
            return None
```

- [ ] **Step 3: 验证**

运行 `python3 main.py`，确认警戒值输入框出现在行合计和数值之间。

- [ ] **Step 4: 提交**

```bash
git add ui/input_bar.py
git commit -m "feat: InputBar 新增警戒值输入框和 get_alert_threshold 方法"
```

---

### Task 2: TableView.refresh() 支持警戒列标红

**Files:**
- Modify: `ui/table_view.py`

**Interfaces:**
- Consumes: `alert_cols: set[int] | None` — 列号集合（1-based），None 或空集合表示无警戒列
- Modifies: `refresh()` 方法签名和数据单元格/表头绘制逻辑

- [ ] **Step 1: 修改 `refresh()` 签名**

```python
    def refresh(self, matrix: list[list], handler, alert_cols: set | None = None):
```

- [ ] **Step 2: 修改列表头绘制逻辑（表头标红）**

在列表头绘制循环中（约第 153-160 行），根据 `alert_cols` 判断颜色：

```python
        # 列表头 — pin_top only
        for ci in range(1, self._num_cols + 1):
            x = self._col_x(ci)
            is_alert = alert_cols and ci in alert_cols
            header_fill = "#ffe0e0" if is_alert else "#e8e8e8"
            header_outline = "#e0a0a0" if is_alert else "#c0c0c0"
            text_fill = "#cc0000" if is_alert else "#333"
            self.canvas.create_rectangle(x, 0, x + COL_W, HEADER_H,
                                         fill=header_fill, outline=header_outline,
                                         tags=("pin_top",))
            self.canvas.create_text(x + COL_W // 2, HEADER_H // 2,
                                    text=col_letter(ci), fill=text_fill,
                                    font=self._font_bold, tags=("pin_top",))
```

- [ ] **Step 3: 修改数据单元格绘制逻辑（单元格标红）**

在数据单元格绘制循环中（约第 180-195 行），根据 `alert_cols` 判断颜色：

```python
        # ── 数据单元格 ──
        for r_idx, row_data in enumerate(matrix):
            r = r_idx + 1
            y = self._row_y(r)
            for c_idx, val in enumerate(row_data):
                c = c_idx + 1
                x = self._col_x(c)
                text = str(val) if val is not None else ""
                display = text[:16] + "…" if len(text) > 17 else text

                is_alert = alert_cols and c in alert_cols
                cell_fill = "#ffe0e0" if is_alert else "white"
                cell_outline = "#e0a0a0" if is_alert else "#e0e0e0"
                cell_text_fill = "#cc0000" if is_alert else "#222"

                tag = f"cell_{r}_{c}"
                self.canvas.create_rectangle(x, y, x + COL_W, y + ROW_H,
                                             fill=cell_fill, outline=cell_outline,
                                             tags=("cell", tag))
                self.canvas.create_text(x + COL_W // 2, y + ROW_H // 2,
                                        text=display, fill=cell_text_fill, font=self._font,
                                        tags=("cell", tag))
```

- [ ] **Step 4: 验证**

运行 `python3 main.py`，打开一个 Excel 文件，切换到固定行模式，设置警戒值为 50，确认超过 50 的列标红。

- [ ] **Step 5: 提交**

```bash
git add ui/table_view.py
git commit -m "feat: TableView.refresh() 支持 alert_cols 参数实现警戒列标红"
```

---

### Task 3: App 层连接警戒值逻辑

**Files:**
- Modify: `ui/app.py`

**Interfaces:**
- Consumes: `InputBar.get_alert_threshold() -> int | None`，`TableView.refresh(matrix, handler, alert_cols)`
- Produces: `App._compute_alert_cols() -> set[int]`

- [ ] **Step 1: 新增 `_compute_alert_cols()` 方法**

在 `_update_row_sum` 方法之后新增：

```python
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
                        alert_cols.add(c_idx + 1)  # 列号从 1 开始
                except (ValueError, TypeError):
                    pass
        return alert_cols
```

- [ ] **Step 2: 修改 `_refresh_table()`**

将警戒列计算传入 `refresh()`：

```python
    def _refresh_table(self):
        alert_cols = self._compute_alert_cols()
        self.table_view.refresh(self.handler.get_matrix(), self.handler, alert_cols)
```

- [ ] **Step 3: 验证**

运行 `python3 main.py`，完整测试流程：
1. 打开一个有数据的 Excel 文件
2. 切换到固定行模式，锁定某行
3. 在警戒值输入框输入一个数值（如 50）
4. 确认超过该值的列整列标红（含表头）
5. 清空警戒值，确认标红消失
6. 切换到非固定行模式，确认标红消失

- [ ] **Step 4: 提交**

```bash
git add ui/app.py
git commit -m "feat: App 层连接警戒值逻辑，_compute_alert_cols 联动 InputBar 和 TableView"
```
