# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 运行

```bash
pip install -r requirements.txt
python3 main.py
```

项目需要系统支持 tkinter。Linux 下确保安装了 `python3-tk`（或 conda 环境自带）。

## 架构

三层结构，`main.py` → `ui/` → `core/`：

```
main.py          # 入口，创建 Tk root 和 App
core/
  excel_handler.py  # openpyxl 封装：读写 .xlsx、获取矩阵
  navigator.py      # 录入模式（逐格/按列递增/按行递增）+ 光标位置
  utils.py          # col_letter(1→A, 27→AA)
ui/
  app.py            # 主窗口：组装组件、菜单、快捷键、回调编排
  input_bar.py      # 输入栏：列号+行号+数值 Entry + 录入按钮
  table_view.py     # 表格视图：Canvas 绘制（非 Treeview），支持 55+ 列不卡
  mode_bar.py       # 模式栏：三个 RadioButton
```

**数据流：** 用户输入 → `InputBar._handle_submit()` → `App._on_submit(col, row, value)` → `ExcelHandler.write_cell()` → `TableView.refresh(matrix)` 重绘。Navigator 在每次写入后调用 `advance()` 决定下次光标位置。

## 关键设计决策

### Canvas 绘制而非 Treeview

`table_view.py` 使用 `tk.Canvas` 绘制表格（`create_rectangle` + `create_text`），不用 `ttk.Treeview`。原因：
- Canvas 支持**单格级高亮**（深色边框 + 浅蓝底色），Treeview 只能行级
- Canvas 图形对象是轻量的，55+ 列不卡

代价：Canvas 在 Linux/X11 下对 CJK 字体支持不稳定，需通过 `app.py._setup_fonts()` 在启动时配置 `TkDefaultFont` 为系统可用的中文字体，Canvas 内部使用 `font=(family, size, "normal")` 元组引用。

### 表头和行号列悬浮固定

`_pin()` 方法在每次滚动事件后执行，将带 `pin_top` tag 的 item 移到视口顶部（表头），带 `pin_left` tag 的 item 移到视口左侧（行号列+分隔线）。xscroll 和 yscroll 都触发 `_pin()`。

### 列号解析

InputBar 的 `_parse_col()` 支持数字（`3`）和字母（`C`、`AA`—即 27）两种输入格式，统一转为 1-based 数字索引传给 ExcelHandler。

### 字体选择策略

`app.py._find_font()` 按优先级查找第一个系统可用的中文字体：Noto Sans CJK SC → WenQuanYi → Noto Sans SC → DejaVu Sans。找到的字体同时配置给 `TkDefaultFont`（tkinter 标准控件）和 Canvas 的 font 元组。
