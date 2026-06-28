# Excel 快速录入工具 — 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建基于 Python + tkinter 的桌面应用，通过三输入框（列号、行号、数值）+ 回车快速向 .xlsx 文件写入数据。

**Architecture:** main.py 入口 → ui/app.py 主窗口组装三个子组件（input_bar, table_view, mode_bar）→ core/ 层处理 Excel 读写（openpyxl）和录入模式导航逻辑。

**Tech Stack:** Python 3.8+, tkinter（标准库）, openpyxl

## Global Constraints

- 所有文件名、路径与设计文档一致
- 使用 pack 布局管理器
- 列号支持字母(A-ZZ)和数字两种输入
- 支持 .xlsx 格式
- 纯键盘操作优先，鼠标为辅

---

## File Structure

```
input_execl/
├── main.py              # 入口
├── ui/
│   ├── __init__.py      # 空
│   ├── app.py           # 主窗口
│   ├── input_bar.py     # 输入栏组件
│   ├── table_view.py    # 表格视图组件
│   └── mode_bar.py      # 模式切换栏
├── core/
│   ├── __init__.py      # 空
│   ├── excel_handler.py # Excel 读写
│   └── navigator.py     # 录入模式逻辑
└── requirements.txt     # openpyxl
```

---

### Task 1: 项目骨架与依赖

**Files:**
- Create: `requirements.txt`
- Create: `main.py`
- Create: `core/__init__.py`
- Create: `ui/__init__.py`

**Interfaces:**
- Produces: 项目可运行的空窗口框架，`core/` 和 `ui/` 包可被 import

- [ ] **Step 1: 创建 requirements.txt**

```bash
cd /home/haoshuai/code/input_execl && mkdir -p core ui
```

```bash
cat > /home/haoshuai/code/input_execl/requirements.txt << 'EOF'
openpyxl>=3.0.0
EOF
```

- [ ] **Step 2: 安装依赖**

```bash
pip install -r requirements.txt
```

- [ ] **Step 3: 创建 `__init__.py` 文件**

`core/__init__.py`:
```python
```

`ui/__init__.py`:
```python
```

- [ ] **Step 4: 创建 main.py 入口**

```python
"""Excel 快速录入工具 — 入口"""
import tkinter as tk
from ui.app import App


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: 创建 ui/app.py 骨架（验证运行）**

```python
"""主窗口"""
import tkinter as tk


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Excel 快速录入工具")
        self.root.geometry("900x600")

        # 临时占位标签，后续任务会替换
        label = tk.Label(root, text="Excel 快速录入工具", font=("", 20))
        label.pack(pady=50)
```

- [ ] **Step 6: 验证运行**

```bash
cd /home/haoshuai/code/input_execl && timeout 3 python main.py 2>&1 || true
```
期望：窗口弹出，标题 "Excel 快速录入工具"，3 秒后自动退出。

- [ ] **Step 7: 提交（可选，如需版本控制）**

---

### Task 2: Excel 读写模块

**Files:**
- Create: `core/excel_handler.py`

**Interfaces:**
- Produces:
  - `class ExcelHandler` — 管理一个 openpyxl Workbook
  - `__init__(self, filepath: str | None = None)` — 加载已有文件或创建新文件
  - `write_cell(self, col: int, row: int, value)` — 写入单元格（col, row 从 1 开始）
  - `read_cell(self, col: int, row: int) -> str` — 读取单元格值
  - `save(self)` — 保存到 filepath
  - `save_as(self, filepath: str)` — 另存为
  - `filepath: str | None` — 当前文件路径
  - `sheet` — openpyxl 当前活动工作表（只读访问）
  - `max_col: int`, `max_row: int` — 当前数据区域的最大行列
  - `get_matrix(self) -> list[list]` — 获取整个表格的二维数组（用于 Treeview 渲染）

- [ ] **Step 1: 实现 core/excel_handler.py**

```python
"""Excel 文件读写处理"""
from pathlib import Path
from openpyxl import Workbook, load_workbook


class ExcelHandler:
    """管理 Excel 工作簿的读写"""

    def __init__(self, filepath: str | None = None):
        self._filepath: str | None = None
        if filepath and Path(filepath).exists():
            self._wb = load_workbook(filepath)
            self._filepath = filepath
        else:
            self._wb = Workbook()
            self._wb.active.title = "Sheet1"

    @property
    def filepath(self) -> str | None:
        return self._filepath

    @property
    def sheet(self):
        return self._wb.active

    @property
    def max_col(self) -> int:
        """返回当前 sheet 的数据最大列数（至少 1）"""
        mc = self.sheet.max_column
        return mc if mc else 1

    @property
    def max_row(self) -> int:
        """返回当前 sheet 的数据最大行数（至少 1）"""
        mr = self.sheet.max_row
        return mr if mr else 1

    def write_cell(self, col: int, row: int, value):
        """写入单元格，col/row 从 1 开始"""
        self.sheet.cell(row=row, column=col, value=value)

    def read_cell(self, col: int, row: int):
        """读取单元格值，返回字符串或 None"""
        cell = self.sheet.cell(row=row, column=col)
        return cell.value

    def get_matrix(self) -> list[list]:
        """获取整个数据区域的二维矩阵
        返回 list[list]，matrix[row][col]，索引从 0 开始
        """
        mr = self.max_row
        mc = self.max_col
        matrix = []
        for r in range(1, mr + 1):
            row_data = []
            for c in range(1, mc + 1):
                val = self.read_cell(c, r)
                row_data.append(val if val is not None else "")
            matrix.append(row_data)
        return matrix

    def save(self):
        """保存到当前文件，如未指定路径则调用 save_as"""
        if self._filepath:
            self._wb.save(self._filepath)
        else:
            raise ValueError("未指定文件路径，请使用 save_as")

    def save_as(self, filepath: str):
        """另存为新文件"""
        self._filepath = filepath
        self._wb.save(filepath)

    def new(self):
        """新建空白工作簿"""
        self._filepath = None
        self._wb = Workbook()
        self._wb.active.title = "Sheet1"
```

- [ ] **Step 2: 手动验证**

```bash
cd /home/haoshuai/code/input_execl && python3 -c "
from core.excel_handler import ExcelHandler
h = ExcelHandler()
h.write_cell(3, 5, 'hello')
assert h.read_cell(3, 5) == 'hello'
h.write_cell(1, 1, 100)
m = h.get_matrix()
assert m[0][0] == 100
assert m[4][2] == 'hello'
h.save_as('/tmp/test_output.xlsx')
print('OK: 所有断言通过')
"
```

---

### Task 3: 录入模式导航模块

**Files:**
- Create: `core/navigator.py`

**Interfaces:**
- Produces:
  - `MODE_SINGLE = "single"` — 逐格录入
  - `MODE_COL_INC = "col_inc"` — 按列递增（行号自动+1）
  - `MODE_ROW_INC = "row_inc"` — 按行递增（列号自动+1）
  - `class Navigator` — 管理当前模式和光标位置
  - `__init__(self)` — 默认逐格模式，(col=1, row=1)
  - `advance(self) -> (int, int)` — 根据当前模式返回下一个写入位置，并更新内部状态
  - `set_position(self, col: int, row: int)` — 手动设置位置
  - `reset(self)` — 重置到 (1, 1)
  - `mode: str` — 当前模式
  - `col: int`, `row: int` — 当前位置

- [ ] **Step 1: 实现 core/navigator.py**

```python
"""录入模式导航逻辑"""

MODE_SINGLE = "single"
MODE_COL_INC = "col_inc"
MODE_ROW_INC = "row_inc"

MODES = [MODE_SINGLE, MODE_COL_INC, MODE_ROW_INC]

MODE_LABELS = {
    MODE_SINGLE: "逐格录入",
    MODE_COL_INC: "按列递增",
    MODE_ROW_INC: "按行递增",
}


class Navigator:
    """管理录入模式和光标位置"""

    def __init__(self):
        self.mode = MODE_SINGLE
        self.col = 1
        self.row = 1

    def set_mode(self, mode: str):
        if mode not in MODES:
            raise ValueError(f"无效模式: {mode}")
        self.mode = mode

    def set_position(self, col: int, row: int):
        self.col = col
        self.row = row

    def reset(self):
        self.col = 1
        self.row = 1

    def advance(self) -> tuple[int, int]:
        """返回下一个写入位置 (col, row)，并根据模式更新状态"""
        if self.mode == MODE_COL_INC:
            self.row += 1
        elif self.mode == MODE_ROW_INC:
            self.col += 1
        # MODE_SINGLE 不自动推进
        return self.col, self.row
```

- [ ] **Step 2: 手动验证**

```bash
cd /home/haoshuai/code/input_execl && python3 -c "
from core.navigator import Navigator, MODE_SINGLE, MODE_COL_INC, MODE_ROW_INC

nav = Navigator()
assert nav.mode == MODE_SINGLE
assert nav.col == 1 and nav.row == 1

# 设置位置
nav.set_position(3, 5)
assert nav.col == 3 and nav.row == 5

# 按列递增
nav.set_mode(MODE_COL_INC)
pos = nav.advance()
assert pos == (3, 6), f'expected (3,6) got {pos}'
assert nav.row == 6

# 按行递增
nav.set_mode(MODE_ROW_INC)
pos = nav.advance()
assert pos == (4, 6), f'expected (4,6) got {pos}'
assert nav.col == 4

# 逐格不递增
nav.set_mode(MODE_SINGLE)
old_col, old_row = nav.col, nav.row
pos = nav.advance()
assert pos == (old_col, old_row)

nav.reset()
assert nav.col == 1 and nav.row == 1

print('OK: 所有断言通过')
"
```

---

### Task 4: 输入栏组件 (InputBar)

**Files:**
- Create: `ui/input_bar.py`
- Modify: `ui/app.py`

**Interfaces:**
- Consumes: `Navigator`（来自 Task 3）
- Produces:
  - `class InputBar(tk.Frame)` — 输入栏组件
  - `__init__(self, parent, on_submit: callable, on_cell_change: callable | None = None)`
  - `on_submit(col: int, row: int, value: str)` — 用户按回车/点击录入按钮时回调
  - `on_cell_change(col: int, row: int)` — 列号或行号变化时通知（用于高亮）
  - `set_col(val)` / `set_row(val)` / `set_value(val)` — 外部设置输入框值
  - `set_column(col: int)` — 设置列号（数字 → 自动转字母或原样）
  - `set_row(row: int)` — 设置行号
  - `focus_value()` — 焦点跳到数值框
  - `clear_value()` — 清空数值框
  - `clear_all()` — 清空所有输入框

- [ ] **Step 1: 实现 ui/input_bar.py**

```python
"""输入栏组件 — 列号、行号、数值输入框 + 录入按钮"""
import tkinter as tk
from tkinter import ttk


class InputBar(tk.Frame):
    def __init__(self, parent, on_submit: callable, on_cell_change: callable | None = None):
        super().__init__(parent)
        self._on_submit = on_submit
        self._on_cell_change = on_cell_change

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

        # 绑定键盘事件
        self.col_entry.bind("<Return>", lambda e: self.row_entry.focus_set())
        self.row_entry.bind("<Return>", lambda e: self.value_entry.focus_set())
        self.value_entry.bind("<Return>", lambda e: self._handle_submit())
        self.col_entry.bind("<Tab>", self._on_tab)
        self.row_entry.bind("<Tab>", self._on_tab)

        # 列号/行号变化时通知 table_view 高亮
        self.col_entry.bind("<KeyRelease>", self._notify_cell_change)
        self.row_entry.bind("<KeyRelease>", self._notify_cell_change)

    def _on_tab(self, event):
        """Tab 切换到下一个输入框"""
        current = event.widget
        if current == self.col_entry:
            self.row_entry.focus_set()
        elif current == self.row_entry:
            self.value_entry.focus_set()
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

        # 恢复正常背景
        self.col_entry.config(bg="white")
        self.row_entry.config(bg="white")

        self._on_submit(col, row, value)

    def set_column(self, col: int):
        self.col_entry.delete(0, tk.END)
        self.col_entry.insert(0, str(col))

    def set_row(self, row: int):
        self.row_entry.delete(0, tk.END)
        self.row_entry.insert(0, str(row))

    def set_value(self, val):
        self.value_entry.delete(0, tk.END)
        self.value_entry.insert(0, str(val) if val is not None else "")

    def focus_value(self):
        self.value_entry.focus_set()

    def clear_value(self):
        self.value_entry.delete(0, tk.END)

    def clear_all(self):
        self.col_entry.delete(0, tk.END)
        self.row_entry.delete(0, tk.END)
        self.value_entry.delete(0, tk.END)
```

- [ ] **Step 2: 更新 ui/app.py 挂载 InputBar**

修改 `ui/app.py`，替换为：

```python
"""主窗口"""
import tkinter as tk
from ui.input_bar import InputBar
from core.excel_handler import ExcelHandler
from core.navigator import Navigator


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Excel 快速录入工具")
        self.root.geometry("900x600")

        self.handler = ExcelHandler()
        self.navigator = Navigator()

        # 输入栏
        self.input_bar = InputBar(
            self.root,
            on_submit=self._on_submit,
            on_cell_change=self._on_cell_change,
        )
        self.input_bar.pack(fill=tk.X, padx=10, pady=(10, 5))

        self._update_title()

    def _on_submit(self, col: int, row: int, value: str):
        self.handler.write_cell(col, row, value)
        self.navigator.set_position(col, row)
        # 根据模式推进位置
        next_col, next_row = self.navigator.advance()
        self.input_bar.set_column(next_col)
        self.input_bar.set_row(next_row)
        self.input_bar.clear_value()
        self.input_bar.focus_value()

    def _on_cell_change(self, col: int, row: int):
        pass  # 后续 task 中连接 table_view 高亮

    def _update_title(self):
        fp = self.handler.filepath
        name = fp if fp else "未命名"
        self.root.title(f"Excel 快速录入工具 — {name}")
```

- [ ] **Step 3: 验证运行**

```bash
cd /home/haoshuai/code/input_execl && timeout 3 python main.py 2>&1 || true
```
期望：窗口显示输入栏，可输入，无报错退出。

---

### Task 5: 表格视图组件 (TableView)

**Files:**
- Create: `ui/table_view.py`
- Modify: `ui/app.py`

**Interfaces:**
- Consumes: `ExcelHandler.get_matrix()`
- Produces:
  - `class TableView(tk.Frame)` — 表格视图
  - `__init__(self, parent, on_cell_click: callable)`
  - `on_cell_click(col: int, row: int)` — 用户点击单元格时回调
  - `refresh(matrix: list[list], handler: ExcelHandler)` — 刷新表格数据
  - `highlight(col: int, row: int)` — 高亮指定单元格
  - `scroll_to(col: int, row: int)` — 滚动到指定单元格可见

- [ ] **Step 1: 实现 ui/table_view.py**

```python
"""表格视图组件 — 基于 ttk.Treeview 展示 Excel 内容"""
import tkinter as tk
from tkinter import ttk


class TableView(tk.Frame):
    def __init__(self, parent, on_cell_click: callable):
        super().__init__(parent)
        self._on_cell_click = on_cell_click
        self._data: list[list] = []
        self._current_highlight: tuple[int, int] | None = None

        # 滚动条
        self.v_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.h_scroll = ttk.Scrollbar(self, orient=tk.HORIZONTAL)

        # Treeview
        self.tree = ttk.Treeview(
            self,
            yscrollcommand=self.v_scroll.set,
            xscrollcommand=self.h_scroll.set,
            show="headings",
        )
        self.v_scroll.config(command=self.tree.yview)
        self.h_scroll.config(command=self.tree.xview)

        # 布局
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 绑定点击
        self.tree.bind("<ButtonRelease-1>", self._on_click)

        # 样式
        style = ttk.Style()
        style.configure("Treeview", rowheight=28)

    def _column_letter(self, n: int) -> str:
        """数字列号 → 字母列号（1→A, 27→AA）"""
        result = ""
        while n > 0:
            n -= 1
            result = chr(n % 26 + ord("A")) + result
            n //= 26
        return result

    def refresh(self, matrix: list[list], handler):
        """完全重建表格"""
        self._data = matrix
        self._handler = handler

        # 清除旧数据
        self.tree.delete(*self.tree.get_children())
        cols = self.tree["columns"]
        self.tree["displaycolumns"] = ()

        if not matrix:
            return

        num_cols = len(matrix[0]) if matrix else 0
        if num_cols == 0:
            return

        # 设置列：col0 = 行号, col1..colN = A, B, C...
        column_ids = ["#0"]  # row header placeholder
        display_cols = []
        for i in range(num_cols):
            col_id = f"col_{i}"
            column_ids.append(col_id)
            display_cols.append(col_id)

        self.tree["columns"] = column_ids[1:]  # tkinter columns excludes #0
        self.tree.column("#0", width=50, anchor="center")
        self.tree.heading("#0", text="")

        for i in range(num_cols):
            col_id = f"col_{i}"
            letter = self._column_letter(i + 1)
            self.tree.column(col_id, width=80, anchor="center", minwidth=60)
            self.tree.heading(col_id, text=letter)

        # 插入行
        for r_idx, row_data in enumerate(matrix):
            row_num = r_idx + 1
            values = [str(v) if v is not None else "" for v in row_data]
            self.tree.insert("", tk.END, iid=str(row_num), text=str(row_num), values=values)

    def _on_click(self, event):
        """点击单元格 → 解析行列 → 回调"""
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return

        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)

        if not row_id or not col_id:
            return

        row = int(row_id)
        col = int(col_id.lstrip("#"))  # col_id 是 "#N" 格式

        self._on_cell_click(col, row)

    def highlight(self, col: int, row: int):
        """高亮指定单元格"""
        # 清除旧高亮
        if self._current_highlight:
            old_col, old_row = self._current_highlight
            try:
                row_id = str(old_row)
                col_id = f"col_{old_col - 1}"
                if self.tree.exists(row_id):
                    self.tree.tag_del(f"highlight_{old_row}_{old_col}")
            except Exception:
                pass

        # 设置新高亮
        try:
            row_id = str(row)
            col_id = f"col_{col - 1}"
            tag = f"highlight_{row}_{col}"
            self.tree.tag_configure(tag, background="#cce5ff")
            self.tree.item(row_id, tags=(tag,))
            self._current_highlight = (col, row)
        except Exception:
            pass

    def scroll_to(self, col: int, row: int):
        """滚动到指定单元格可见"""
        try:
            row_id = str(row)
            if self.tree.exists(row_id):
                self.tree.see(row_id)
        except Exception:
            pass
```

- [ ] **Step 2: 更新 ui/app.py 集成 TableView**

用以下完整版本替换 `ui/app.py`：

```python
"""主窗口"""
import tkinter as tk
from tkinter import filedialog, messagebox
from ui.input_bar import InputBar
from ui.table_view import TableView
from ui.mode_bar import ModeBar
from core.excel_handler import ExcelHandler
from core.navigator import Navigator, MODE_SINGLE, MODE_COL_INC, MODE_ROW_INC, MODE_LABELS


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Excel 快速录入工具")
        self.root.geometry("1000x650")
        self.root.minsize(600, 400)

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
        self.table_view = TableView(self.root, on_cell_click=self._on_cell_click)
        self.table_view.pack(fill=tk.BOTH, expand=True, padx=10, pady=2)
        self._refresh_table()

        # 模式栏
        self.mode_bar = ModeBar(self.root, on_mode_change=self._on_mode_change)
        self.mode_bar.pack(fill=tk.X, padx=10, pady=2)

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(
            self.root, textvariable=self.status_var,
            anchor=tk.W, relief=tk.SUNKEN, font=("", 9)
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self._update_status()

        # 快捷键
        self._bind_shortcuts()

        self._update_title()

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

    # ── 快捷键 ──

    def _bind_shortcuts(self):
        self.root.bind("<Control-o>", lambda e: self._file_open())
        self.root.bind("<Control-s>", lambda e: self._file_save())
        self.root.bind("<Control-n>", lambda e: self._file_new())
        self.root.bind("<Control-Key-1>", lambda e: self._set_mode(MODE_SINGLE))
        self.root.bind("<Control-Key-2>", lambda e: self._set_mode(MODE_COL_INC))
        self.root.bind("<Control-Key-3>", lambda e: self._set_mode(MODE_ROW_INC))
        self.root.bind("<Escape>", lambda e: self.input_bar.clear_all())

    # ── 文件操作 ──

    def _file_new(self):
        self.handler.new()
        self.navigator.reset()
        self.input_bar.clear_all()
        self.input_bar.set_column(1)
        self.input_bar.set_row(1)
        self._refresh_table()
        self._update_title()
        self._update_status()

    def _file_open(self):
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
        self.handler.write_cell(col, row, value)
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

        self._update_status(f"已写入 {self._col_letter(col)}{row} = {value}")

    def _on_cell_change(self, col: int, row: int):
        """输入栏列号/行号变化时高亮对应单元格"""
        self.table_view.highlight(col, row)

    def _on_cell_click(self, col: int, row: int):
        """表格单元格被点击 → 填充输入栏"""
        self.input_bar.set_column(col)
        self.input_bar.set_row(row)
        self.table_view.highlight(col, row)
        self.input_bar.focus_value()

    def _on_mode_change(self, mode: str):
        self.navigator.set_mode(mode)
        self._update_status()

    # ── 辅助方法 ──

    def _refresh_table(self):
        self.table_view.refresh(self.handler.get_matrix(), self.handler)

    def _set_mode(self, mode: str):
        self.navigator.set_mode(mode)
        self.mode_bar.set_mode(mode)
        self._update_status()

    def _update_title(self):
        fp = self.handler.filepath
        name = fp.split("/")[-1] if fp else "未命名"
        self.root.title(f"Excel 快速录入工具 — {name}")

    def _update_status(self, msg: str | None = None):
        fp = self.handler.filepath
        name = fp.split("/")[-1] if fp else "未命名"
        saved = "已保存" if fp else "未保存"
        pos = f"{self._col_letter(self.navigator.col)}{self.navigator.row}"
        mode_label = MODE_LABELS.get(self.navigator.mode, self.navigator.mode)
        self.status_var.set(
            f"  {name} | {saved} | 位置: {pos} | 模式: {mode_label}"
            + (f" | {msg}" if msg else "")
        )

    @staticmethod
    def _col_letter(n: int) -> str:
        result = ""
        while n > 0:
            n -= 1
            result = chr(n % 26 + ord("A")) + result
            n //= 26
        return result
```

- [ ] **Step 3: 创建 ui/mode_bar.py 骨架（避免 import 报错）**

```python
"""模式切换栏 — 逐格/按列递增/按行递增"""
import tkinter as tk
from core.navigator import MODE_SINGLE, MODE_COL_INC, MODE_ROW_INC, MODE_LABELS


class ModeBar(tk.Frame):
    def __init__(self, parent, on_mode_change: callable):
        super().__init__(parent)
        self._on_mode_change = on_mode_change
        self._var = tk.StringVar(value=MODE_SINGLE)

        tk.Label(self, text="模式:").pack(side=tk.LEFT, padx=(0, 10))

        for mode in [MODE_SINGLE, MODE_COL_INC, MODE_ROW_INC]:
            rb = tk.Radiobutton(
                self, text=MODE_LABELS[mode], variable=self._var,
                value=mode, command=self._changed
            )
            rb.pack(side=tk.LEFT, padx=5)

    def _changed(self):
        self._on_mode_change(self._var.get())

    def set_mode(self, mode: str):
        self._var.set(mode)
```

- [ ] **Step 4: 验证运行**

```bash
cd /home/haoshuai/code/input_execl && timeout 4 python main.py 2>&1 || true
```
期望：窗口显示完整界面（输入栏 + 空表格 + 模式栏 + 状态栏），4 秒后自动退出。

---

### Task 6: 端到端集成测试与完善

**Files:**
- Modify: `ui/app.py`, `ui/table_view.py`, `ui/input_bar.py`

**目标：** 修复集成中发现的问题，完善细节。

- [ ] **Step 1: 端到端手动测试**

```bash
cd /home/haoshuai/code/input_execl && timeout 5 python main.py 2>&1 || true
```

按以下顺序在窗口中操作：
1. 确认输入栏、表格、模式栏、状态栏正常显示
2. 在列号输入 C，行号输入 5，数值输入 test123，回车
3. 确认状态栏显示 "已写入 C5 = test123"
4. 确认表格视图中 C 列第 5 行显示 test123
5. 切换到"按列递增"模式，再输入值，确认行号自动+1
6. Ctrl+O 打开文件、Ctrl+S 保存

- [ ] **Step 2: 修复 Treeview 行号列宽问题**

在 `ui/table_view.py` 的 `refresh()` 方法中，确保行号列宽度合适：

```python
# refresh() 中，将
self.tree.column("#0", width=50, anchor="center")
# 改为根据最大行号动态调整：
max_row = len(matrix)
row_header_width = max(50, len(str(max_row)) * 12 + 20)
self.tree.column("#0", width=row_header_width, anchor="center")
```

- [ ] **Step 3: 修复保存后仍显示"未保存"**

`_file_save` 后需刷新状态栏。已在上面的 `_file_save` 中调用 `_update_status("已保存")`，确认即可。

- [ ] **Step 4: 最终验证清单**

- [ ] 新建 → 输入数据 → 表格刷新 ✅
- [ ] 保存 → 另存为 → 用 Excel 打开验证 ✅
- [ ] 打开已有 .xlsx → 表格正确显示 ✅
- [ ] 三种模式切换正常 ✅
- [ ] 快捷键都生效 ✅
- [ ] 点击单元格自动填充列号行号 ✅
