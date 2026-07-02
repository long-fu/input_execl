# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 运行

```bash
# 首次：创建虚拟环境并安装依赖
python3 -m venv .venv
source .venv/bin/activate   # Linux
.venv/bin/pip install -r requirements.txt

# 运行（需要 tkinter 支持）
.venv/bin/python3 main.py
```

项目需要系统支持 tkinter。Linux 下确保安装了 `python3-tk`（或 conda 环境自带）。

## 打包为 EXE

```bash
.venv/bin/pip install pyinstaller
.venv/bin/pyinstaller --onefile --name excel_input --add-data "core;core" --add-data "ui;ui" main.py
# Windows 路径分隔符用 ;（如 core;core），Linux 用 :（core:core）
```

GitHub Actions 工作流在 `.github/workflows/build-exe.yml`，仅在 `feat/fixed-row-mode` 分支 push 时触发，构建 Windows EXE 并上传为 artifact。

## 测试

项目目前没有自动化测试。验证方式为手动运行应用。

## 架构

三层结构，`main.py` → `ui/` → `core/`：

```
main.py          # 入口，创建 Tk root 和 App
core/
  excel_handler.py  # openpyxl 封装：读写 .xlsx、获取矩阵、新建/保存
  navigator.py      # 四种录入模式 + 光标位置
  utils.py          # col_letter(1→A, 27→AA)
ui/
  app.py            # 主窗口：组装组件、菜单、快捷键、回调编排、警戒逻辑
  input_bar.py      # 输入栏：列号+行号+数值+警戒值+锁定复选框+清空行+撤销
  table_view.py     # 表格视图：Canvas 绘制（非 Treeview），支持 55+ 列不卡
  mode_bar.py       # 模式栏：四个 RadioButton（当前已隐藏，通过复选框切换）
```

**数据流（主路径）：** 用户输入 → `InputBar._handle_submit()` → `App._on_submit(col, row, value)` → `ExcelHandler.write_cell()` → `TableView.refresh(matrix)` 重绘。Navigator 在每次写入后调用 `advance()` 决定下次光标位置。

**数据流（辅助路径）：**
- 列号/行号变化 → `InputBar._notify_cell_change()` → `App._on_cell_change()` → `TableView.highlight()` + `scroll_to()`（实时高亮）
- 点击表格单元格 → `TableView._on_click()` → `App._on_cell_click()` → 填充 InputBar 列号/行号/当前值
- 撤销 (Ctrl+Z) → `App._undo()` → pop 撤销栈 → 恢复旧值 + 删除记录面板最后一行

## 四种录入模式

| 模式 | 常量 | 行为 |
|------|------|------|
| 逐格录入 | `MODE_SINGLE` | 写入后不自动推进，光标回到列号框 |
| 按列递增 | `MODE_COL_INC` | 写入后行号+1 |
| 按行递增 | `MODE_ROW_INC` | 写入后列号+1 |
| 固定行 | `MODE_FIXED_ROW` | 写入后行号保持锁定值，列号清空等待下次输入 |

**固定行模式**是本项目核心功能（`feat/fixed-row-mode` 分支）。行为细节：
- 通过"锁定行号"复选框或 ModeBar 切换进入
- 锁定后行号输入框变为只读（灰色背景）
- 录入后行号不变，列号清空，焦点回到列号框 — 适合对同一行的多列连续录入
- "清空行"按钮可用，清空当前锁定行的所有数据
- 锁定行所有数值合计显示在行号旁（蓝色）
- 点击表格任意单元格会更新固定行目标为该单元格所在行
- 启动时默认不锁定（MODE_SINGLE）

## 警戒值系统

InputBar 包含警戒值输入框，仅在固定行模式下生效：
- 设置警戒值后，`App._compute_alert_cols()` 遍历固定行中所有单元格
- 值超过警戒值的列：表头和单元格均以红色底色（#ffe0e0）和红色文字（#cc0000）渲染
- 右侧"警戒列表"面板以 `列,行=值` 格式列出所有超警戒单元格
- 警戒值为空或非整数时，不启用警戒

## 撤销机制

- `App._undo_stack: list[tuple[int, int, object]]` 存储 `(col, row, old_value)` 
- 每次录入和清空行操作前保存旧值（清空行时从右到左保存以支持从左到右恢复）
- 撤销时 pop 栈顶，恢复旧值，删除输入记录面板最后一行，清空输入栏
- 支持 Ctrl+Z 快捷键和"撤销"按钮

## 右侧面板布局

右侧面板（log_frame）固定在 180px 宽，分为上下两层：
- **上方 60%（输入记录）**：每次录入追加一行 `列号;行号;值`，撤销时删除最后一行
- **下方 40%（警戒列表）**：显示固定行中超过警戒值的所有单元格，格式 `列,行=值`

## ModeBar 状态

`ModeBar` 当前在 `app.py` 中 `pack()` 被注释掉（不显示）。模式切换通过 InputBar 的"锁定行号"复选框实现：勾选 → 固定行模式，取消 → 逐格模式。若未来需要恢复手动模式选择，取消注释 `self.mode_bar.pack(...)` 并同步复选框状态即可。

## 关键设计决策

### Canvas 绘制而非 Treeview

`table_view.py` 使用 `tk.Canvas` 绘制表格（`create_rectangle` + `create_text`），不用 `ttk.Treeview`。原因：
- Canvas 支持**单格级高亮**（深色边框 + 浅蓝底色），Treeview 只能行级
- Canvas 图形对象是轻量的，55+ 列不卡
- Canvas 支持**单格级标红**（警戒系统），可对任意单元格独立着色

代价：Canvas 在 Linux/X11 下对 CJK 字体支持不稳定，需通过 `app.py._setup_fonts()` 在启动时配置 `TkDefaultFont` 为系统可用的中文字体，Canvas 内部使用 `font=(family, size, "normal")` 元组引用。

### 表头和行号列悬浮固定

`_pin()` 方法在每次滚动事件后执行，将带 `pin_top` tag 的 item 移到视口顶部（表头），带 `pin_left` tag 的 item 移到视口左侧（行号列+分隔线）。xscroll 和 yscroll 都触发 `_pin()`。

### 列号解析

InputBar 的 `_parse_col()` 支持数字（`3`）和字母（`C`、`AA`—即 27）两种输入格式，统一转为 1-based 数字索引传给 ExcelHandler。

### 字体选择策略

`app.py._find_font()` 按优先级查找第一个系统可用的中文字体：Noto Sans CJK SC → WenQuanYi → Noto Sans SC → DejaVu Sans。找到的字体同时配置给 `TkDefaultFont`（tkinter 标准控件）和 Canvas 的 font 元组。

### scroll_to 中的 update_idletasks

`TableView.scroll_to()` 在计算滚动位置前调用 `self.update_idletasks()`（Frame 级），确保 grid 布局完成且 `canvas.winfo_width()/height()` 返回准确尺寸。不使用 tk 根级 `update_idletasks()` 以避免不必要的全局副作用。

### 累加写入语义

写入时如果目标单元格已有整数值，新值**累加**到旧值上（而非覆盖）。如果旧值非整数（文本、浮点数等），则覆盖。原始输入值记录到输入记录面板，非累加后结果。
