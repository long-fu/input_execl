# 警戒值功能设计

## 概述

在输入栏中增加一个警戒值输入框。在固定行模式下，当锁定行中某列的值超过警戒值时，该列的整列（含表头和数据单元格）标红。

## 功能要点

- 所有列共用一个警戒值
- 仅在固定行模式（锁定行号）下生效
- 比较对象：锁定行各列的单元格值（累加后结果），与警戒值比较
- 超出警戒值的列：整列标红（表头 + 数据单元格）
- 警戒值输入框为空时，不启用警戒功能

## 组件改动

### InputBar (`ui/input_bar.py`)

在"行合计"后、"数值"前新增警戒值输入框：

```
列号 → 行号 → 行合计 → [警戒值: ___] → 数值 → 清空行 → 撤销 → 锁定行号
```

- 新增 `alert_entry = tk.Entry(self, width=6)`
- 新增 `get_alert_threshold() -> int | None` 方法
- 初始为空

### TableView (`ui/table_view.py`)

`refresh()` 新增 `alert_cols: set[int] | None = None` 参数。

警戒列绘制样式：
- 单元格背景: `#ffe0e0`（浅红）
- 文字颜色: `#cc0000`（深红）
- 边框: `#e0a0a0`
- 表头同色处理

### App (`ui/app.py`)

- 新增 `_compute_alert_cols() -> set[int]` 方法
- `_refresh_table()` 调用前计算警戒列并传入
- `_on_submit()` 提交后重新计算并刷新

## 数据流

```
用户设置警戒值 → InputBar.get_alert_threshold()
                         ↓
App._compute_alert_cols() ← 遍历锁定行各列值
                         ↓
TableView.refresh(matrix, handler, alert_cols) → 绘制红色列
```
