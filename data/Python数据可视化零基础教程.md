# Python 数据可视化零基础教程
## 基于真实业务场景：游戏平台周报数据分析

> 本教程基于真实的周报可视化代码，手把手带你从零开始，学完即可上手工作。

---

## 目录

1. [环境准备：安装必要工具](#1-环境准备)
2. [核心库速查手册](#2-核心库速查手册)
3. [第一关：读取数据](#3-第一关读取数据)
4. [第二关：数据清洗](#4-第二关数据清洗)
5. [第三关：画第一张图——折线图（Top100充值分布）](#5-第三关折线图)
6. [第四关：双轴图——柱状图+折线图（厂商分析）](#6-第四关双轴图)
7. [第五关：自动标注与图例](#7-第五关标注与图例)
8. [第六关：自动结论输出](#8-第六关自动结论)
9. [完整流程串讲](#9-完整流程串讲)
10. [举一反三：常见变形](#10-举一反三)
11. [常见报错与解决方法](#11-常见报错)

---

## 1. 环境准备

### 第一步：安装 Python

去官网 https://www.python.org/downloads/ 下载最新版，安装时勾选 **"Add Python to PATH"**（非常重要！）

### 第二步：安装必要的库

打开命令行（Windows按Win+R输入cmd），依次运行：

```bash
pip install pandas          # 数据处理
pip install numpy           # 数学计算
pip install matplotlib      # 画图
pip install openpyxl        # 读写Excel
pip install xlsxwriter      # 写Excel（更多格式控制）
```

一行搞定版：
```bash
pip install pandas numpy matplotlib openpyxl xlsxwriter
```

### 第三步：推荐使用 VS Code 或 Jupyter Notebook

- VS Code：https://code.visualstudio.com/（推荐，装Python插件）
- Jupyter：`pip install jupyter` 然后运行 `jupyter notebook`

---

## 2. 核心库速查手册

在代码最顶部，你总会看到这些导入语句，它们的作用如下：

```python
import pandas as pd         # pd = 数据表格处理神器，类似Excel操作
import numpy as np          # np = 数学计算，处理数组/空值
import matplotlib.pyplot as plt  # plt = 画图工具
import matplotlib.ticker as mtick    # 格式化坐标轴（如显示%）
import matplotlib.patches as mpatches  # 自定义图例
from matplotlib.lines import Line2D     # 自定义折线图例
```

**记忆口诀：pd管表，np管数，plt管图**

---

## 3. 第一关：读取数据

### 读取 CSV 文件

```python
import pandas as pd

# 读取CSV（路径用 r"..." 防止反斜杠报错）
df = pd.read_csv(r"C:\Users\你的用户名\Downloads\数据文件.csv")

# 查看前5行，确认读进来了
print(df.head())

# 查看所有列名
print(df.columns.tolist())
```

### 读取 Excel 文件

```python
df = pd.read_excel(r"C:\路径\文件.xlsx")
print(df.head())
```

### ⚠️ 新手常见问题：列名有空格

真实数据的列名经常带空格，导致后续操作报错。**标准解决方案**：

```python
# 一行代码去掉所有列名的首尾空格（必做！）
df.columns = df.columns.str.strip()
```

### 自动查找包含关键词的列名

当你不确定列名叫什么时（比如有时叫"充值金额"，有时叫"充值总金额"）：

```python
def find_amount_col(df):
    for col in df.columns:
        if "充值" in col and "金额" in col:
            return col
    raise Exception("没找到充值金额字段，请检查列名")

amount_col = find_amount_col(df)
print("找到的列名：", amount_col)
```

---

## 4. 第二关：数据清洗

真实数据总是"脏"的，必须先清洗再分析。

### 把"-"替换为空值，并转换为数字

```python
import numpy as np

# 把"-"替换为NaN（空值）
df.replace("-", np.nan, inplace=True)

# 把某列强制转换为数字（转不了的变成NaN）
df["充值金额"] = pd.to_numeric(df["充值金额"], errors="coerce")
```

### 处理带逗号的数字（如 1,000,000）

```python
def clean_num(col):
    return pd.to_numeric(
        col.astype(str).str.replace(",", ""),  # 先去掉逗号
        errors='coerce'                          # 转不了的变NaN
    )

df["投注金额"] = clean_num(df["投注金额"])
```

### 处理百分比字符串（如 "12.5%"）

```python
def clean_pct(col):
    return pd.to_numeric(
        col.astype(str).str.replace("%", ""),   # 去掉%号
        errors='coerce'
    )

df["投注额占比"] = clean_pct(df["投注额占比"])
```

### 查看数据基本情况

```python
print(df.shape)        # (行数, 列数)
print(df.dtypes)       # 每列的数据类型
print(df.isnull().sum()) # 每列空值数量
print(df.describe())   # 数值列的统计摘要
```

---

## 5. 第三关：折线图

### 目标：画出近两周Top100充值金额对比折线图

效果：两条折线，一条本周，一条上周，自动标注最大值和最小值。

#### 第一步：排序，取Top100

```python
TOP_N = 100

# 按充值金额降序排序，取前100行
df_this_top = df_this.sort_values("充值金额", ascending=False).head(TOP_N)
df_last_top = df_last.sort_values("充值金额", ascending=False).head(TOP_N)

# 取出数值数组
values_this = df_this_top["充值金额"].values
values_last = df_last_top["充值金额"].values
```

#### 第二步：解决数量不够100的情况

```python
def pad_to_100(arr):
    if len(arr) < TOP_N:
        # 不足100条就补NaN，保证两条线长度一样
        return np.append(arr, [np.nan] * (TOP_N - len(arr)))
    return arr

values_this = pad_to_100(values_this)
values_last = pad_to_100(values_last)
```

#### 第三步：设置中文字体（必做！否则中文显示方块）

```python
plt.rcParams['font.sans-serif'] = ['SimHei']   # Windows用黑体
plt.rcParams['axes.unicode_minus'] = False      # 修复负号显示
```

> **Mac用户**把 `SimHei` 改成 `Arial Unicode MS`

#### 第四步：画基础折线图

```python
plt.figure(figsize=(12, 6))   # 宽12英寸，高6英寸

plt.plot(values_this, marker='o', label="本周Top100")
plt.plot(values_last, marker='o', label="上周Top100")

plt.title("近两周Top100用户充值金额分布对比")
plt.xlabel("用户排名（按充值金额排序）")
plt.ylabel("充值金额")
plt.legend()   # 显示图例
plt.grid(True) # 显示网格

plt.tight_layout()  # 自动调整间距，防止标签被截断
plt.show()
```

#### 第五步：添加最大值/最小值标注

```python
# 找最大值和它的位置
max_this = np.nanmax(values_this)       # 忽略NaN取最大值
max_idx_this = np.nanargmax(values_this) # 最大值的索引位置

# 在最大值处画一个大圆点
plt.scatter(max_idx_this, max_this, s=120)

# 添加文字箭头标注
plt.annotate(
    f"本周最大\n{max_this:,.0f}",        # 标注文字，:,.0f 表示带千分位逗号的整数
    xy=(max_idx_this, max_this),          # 箭头指向的坐标
    xytext=(max_idx_this+3, max_this*1.05), # 文字的位置（稍微偏移）
    arrowprops=dict(arrowstyle="->"),     # 箭头样式
    bbox=dict(boxstyle="round", fc="white")  # 文字背景白色圆角框
)
```

**数字格式化速查**：
- `f"{value:,.0f}"` → 1,234,567（带逗号，无小数）
- `f"{value:.2f}"` → 1234567.89（无逗号，2位小数）
- `f"{value:.2%}"` → 12.34%（自动乘100显示百分比）
- `f"{value:+.2%}"` → +12.34% 或 -5.67%（带正负号）

---

## 6. 第四关：双轴图

双轴图是这套报表的核心图表类型：**左轴显示市场份额（柱状图），右轴显示环比增长率（折线图）**。

### 完整双轴图代码（带详细注释）

```python
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

# ---- 假设数据 ----
厂商名称 = ["Tada", "Pragmatic", "Rectangle", "PG Soft", "Originals"]
本周份额 = [50.81, 15.69, 8.34, 7.05, 3.53]
上周份额 = [50.78, 15.43, 8.51, 7.07, 3.50]
份额变化 = [本周-上周 for 本周, 上周 in zip(本周份额, 上周份额)]
投注环比 = [5.2, 3.9, -4.7, -1.9, 6.3]
盈利环比 = [10.3, -6.8, 21.0, 41.0, 30.6]

x = np.arange(len(厂商名称))

# ---- 创建图形 ----
fig, ax1 = plt.subplots(figsize=(14, 8))

# ---- 根据份额变化设置颜色 ----
colors = [
    '#2ecc71' if c > 0 else '#e74c3c' if c < 0 else '#3498db'
    for c in 份额变化
]
# 解释：份额涨了 → 绿色，跌了 → 红色，不变 → 蓝色

# ---- 画柱状图（左轴）----
bars = ax1.bar(x, 本周份额, width=0.6, color=colors, edgecolor='black')

# 设置左轴
ax1.set_ylabel('市场份额 (%)')
ax1.set_xticks(x)
ax1.set_xticklabels(厂商名称, rotation=45, ha='right')  # 标签旋转45度
ax1.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.2f%%'))  # 格式如 50.81%
ax1.set_ylim(0, max(本周份额) + 10)  # 顶部留空给标签

# 在每个柱子顶部加标签（份额 + 变化量）
for i, bar in enumerate(bars):
    height = bar.get_height()
    变化 = 份额变化[i]
    箭头 = f'↑{变化:.2f}%' if 变化 > 0 else f'↓{abs(变化):.2f}%'
    颜色 = '#2ecc71' if 变化 > 0 else '#e74c3c'
    
    ax1.text(
        bar.get_x() + bar.get_width()/2,  # X坐标：柱子中心
        height + 0.5,                      # Y坐标：柱子顶部稍高
        f'{本周份额[i]:.2f}%  {箭头}',
        ha='center', fontsize=9, fontweight='bold', color=颜色
    )

# 用短横线标出上周份额位置
ax1.scatter(x, 上周份额, color='black', s=50, marker='_')

# ---- 创建右轴 ----
ax2 = ax1.twinx()   # twin = 孪生轴，共用X轴

投注颜色 = '#e67e22'   # 橙色代表投注
盈利颜色 = '#9b59b6'   # 紫色代表盈利

# 画折线
ax2.plot(x, 投注环比, color=投注颜色, marker='o', linewidth=2.5, label='投注环比')
ax2.plot(x, 盈利环比, color=盈利颜色, marker='s', linewidth=2.5, linestyle='--', label='盈利环比')

# 设置右轴范围（动态计算防截断）
所有值 = 投注环比 + 盈利环比
y_min, y_max = min(所有值), max(所有值)
margin = (y_max - y_min) * 0.1
ax2.set_ylim(y_min - margin, y_max + margin)

ax2.set_ylabel('环比增长率 (%)')
ax2.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0f%%'))
ax2.axhline(0, color='black', linewidth=0.8, alpha=0.5)  # 画0%基准线

# 在折线上标注数值
for i, v in enumerate(投注环比):
    ax2.annotate(f'{v:.1f}%', (i, v),
                 textcoords="offset points", xytext=(0, 8),
                 ha='center', fontsize=8, color=投注颜色)

for i, v in enumerate(盈利环比):
    ax2.annotate(f'{v:.1f}%', (i, v),
                 textcoords="offset points", xytext=(0, -12),
                 ha='center', fontsize=8, color=盈利颜色)

plt.title('MX TOP10 游戏厂商分析（份额 + 环比）')
plt.tight_layout()
plt.show()
```

---

## 7. 第五关：标注与图例

### 自定义图例（当有多种图形混合时）

默认图例无法混合"柱子"和"折线"，需要手动构建：

```python
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

legend_elements = [
    # 色块（代表柱状图）
    mpatches.Patch(color='#2ecc71', label='份额增长'),
    mpatches.Patch(color='#e74c3c', label='份额下降'),
    mpatches.Patch(color='#3498db', label='份额持平'),
    
    # 短横线（代表上周份额标记）
    Line2D([0], [0], color='black', marker='_', linewidth=0, markersize=10, label='上周份额'),
    
    # 折线（代表环比）
    Line2D([0], [0], color='#e67e22', marker='o', linewidth=2.5, label='投注环比'),
    Line2D([0], [0], color='#9b59b6', marker='s', linewidth=2.5, linestyle='--', label='盈利环比')
]

ax1.legend(handles=legend_elements, loc='upper right')
```

### 折线标注技巧：截断显示但标注真实值

当数据有极端值（如+1301%）时，折线会被拉飞，其他数据看不清。解决方案：**图形截断，标签显示真实值**。

```python
# 保存原始值
g["投注额环比_原"] = g["投注额环比"].copy()

# 截断显示值（超出范围的压到边界）
g["投注额环比"] = g["投注额环比"].clip(-80, 80)

# 画折线（用截断值，所以不会跑出去）
ax2.plot(x, g["投注额环比"], marker="o")
ax2.set_ylim(-80, 80)

# 标注时用原始值（真实数据）
for i in range(len(g)):
    v = g["投注额环比"].iloc[i]        # 截断后的位置（决定标签画在哪）
    real = g["投注额环比_原"].iloc[i]  # 真实值（显示给用户看）
    ax2.text(i, v + 5, f"{real:.1f}%", ha="center", fontsize=8)
```

---

## 8. 第六关：自动结论

这是最实用的部分——让Python自动帮你写分析结论，不用手动对数据。

### 结构分析模板

```python
def trend_analysis(arr_this, arr_last):
    """
    arr_this: 本周数值数组（已排序）
    arr_last: 上周数值数组（已排序）
    """
    
    # --- 计算各层均值 ---
    top10_this = np.nanmean(arr_this[:10])   # 前10名的均值
    top10_last = np.nanmean(arr_last[:10])
    top100_this = np.nanmean(arr_this)        # 全部100名均值
    top100_last = np.nanmean(arr_last)
    
    # --- 打印对比 ---
    print(f"Top10均值: {top10_last:,.0f} → {top10_this:,.0f} ({(top10_this/top10_last-1):+.2%})")
    print(f"Top100均值: {top100_last:,.0f} → {top100_this:,.0f} ({(top100_this/top100_last-1):+.2%})")
    
    # --- 头部集中度 ---
    top10_ratio_this = np.nansum(arr_this[:10]) / np.nansum(arr_this)
    top10_ratio_last = np.nansum(arr_last[:10]) / np.nansum(arr_last)
    
    # --- 自动判断结论 ---
    if top10_this > top10_last and top100_this <= top100_last:
        print("⚠️ 头部变强，但整体没变 → 更依赖大R（风险上升）")
    elif top10_this < top10_last and top100_this >= top100_last:
        print("⚠️ 大R流失，中小R在撑盘")
    elif top100_this > top100_last and np.nanmean(arr_this[-20:]) > np.nanmean(arr_last[-20:]):
        print("✅ 整体变强，结构健康（优质增长）")
    else:
        print("➡️ 结构变化不明显，但需结合业务判断")
```

### 四象限分析

**思路：投注金额环比（X轴）× 公司输赢环比（Y轴）**，划分四个象限。

```python
for _, row in df_top10.iterrows():
    bet = row["投注金额环比"]     # 投注变化
    profit = row["公司输赢环比"]  # 盈利变化
    name = row["厂商名称"]
    
    if pd.isna(bet) or pd.isna(profit):
        continue
    
    if bet > 0 and profit > 0:
        print(f"✅ {name}：量利齐升（优质增长）")
    elif bet > 0 and profit < 0:
        print(f"⚠️ {name}：规模增长但盈利恶化（高风险）")
    elif bet < 0 and profit > 0:
        print(f"💡 {name}：规模下降但盈利提升（结构优化）")
    elif bet < 0 and profit < 0:
        print(f"❌ {name}：量利双降（需重点关注）")
```

---

## 9. 完整流程串讲

整套报表的逻辑链：

```
读取两个文件（本周/上周）
       ↓
列名清洗（去空格）
       ↓
数值清洗（去逗号、去%、转数字）
       ↓
按厂商聚合（避免重复行干扰）
       ↓
计算派生指标（环比 = (本周-上周)/上周 × 100）
       ↓
排序取Top10/Top100
       ↓
画图（柱状图 + 折线图 + 标注 + 图例）
       ↓
输出Excel（可分享）
       ↓
打印自动结论（四象限 / 集中度 / 趋势判断）
```

### 计算环比的标准写法

```python
import numpy as np

# 安全的环比计算（防止除以0报错）
def calc_rate(new, old):
    return np.where(
        (old == 0) | (pd.isna(old)),  # 如果上周是0或空值
        np.nan,                        # 结果为NaN（不计算）
        (new - old) / old * 100        # 正常计算
    )

df["投注金额环比"] = calc_rate(df["投注金额_本周"], df["投注金额_上周"])
```

---

## 10. 举一反三

学会了这套代码，可以快速变形到以下场景：

### 变形1：换成日报/月报

只需修改文件路径和标题文字：
```python
file_this = r"本月数据.xlsx"
file_last = r"上月数据.xlsx"
plt.title("本月 vs 上月 TOP10厂商分析")
```

### 变形2：换分析维度（如渠道、地区）

修改 `groupby` 的字段名即可：
```python
# 原来按厂商
df.groupby("游戏厂商.名称").agg({"投注金额": "sum"})

# 改成按渠道
df.groupby("渠道名称").agg({"投注金额": "sum"})

# 改成按地区
df.groupby("用户地区").agg({"投注金额": "sum"})
```

### 变形3：多指标折线图

```python
# 原来只画2条线
ax2.plot(x, 投注环比, label="投注环比")
ax2.plot(x, 盈利环比, label="盈利环比")

# 加第3条线（如活跃用户环比）
ax2.plot(x, 用户环比, color='green', marker='^', label="活跃用户环比")
```

### 变形4：自动保存图片（不弹窗）

```python
# 把 plt.show() 替换为 savefig
plt.savefig('厂商分析.png', dpi=300, bbox_inches='tight')
plt.close()  # 关闭图形，防止内存泄漏
```

### 变形5：导出带格式的Excel

```python
with pd.ExcelWriter("输出.xlsx", engine="xlsxwriter") as writer:
    df.to_excel(writer, index=False, sheet_name="TOP10")
    
    worksheet = writer.sheets["TOP10"]
    worksheet.set_column("A:A", 25)   # A列宽25
    worksheet.set_column("B:G", 15)   # B到G列宽15
```

---

## 11. 常见报错

| 报错信息 | 原因 | 解决方法 |
|---------|------|---------|
| `KeyError: '充值金额'` | 列名不存在或有空格 | 先 `print(df.columns.tolist())` 查看，再加 `.str.strip()` |
| `UnicodeDecodeError` | CSV编码问题 | 改为 `pd.read_csv(file, encoding='gbk')` |
| 图表中文显示方块 | 字体未设置 | 加 `plt.rcParams['font.sans-serif'] = ['SimHei']` |
| `ValueError: could not convert string to float` | 数字列里有文字或逗号 | 用 `clean_num()` 函数清洗 |
| `FileNotFoundError` | 路径错误 | 路径加 `r` 前缀：`r"C:\路径"` |
| `ModuleNotFoundError` | 库未安装 | 运行 `pip install 库名` |
| 图表标签被截断 | 图形太小 | 增大 `figsize` 或加 `plt.tight_layout()` |
| 折线被极端值拉飞 | 数据有异常大值 | 用 `.clip(-80, 80)` 截断显示，标签仍显示真实值 |

---

## 总结：你已经学会了什么

✅ **读数据**：`pd.read_csv` / `pd.read_excel`  
✅ **清数据**：去空格、去逗号、去%、转数字、处理空值  
✅ **排序取Top**：`sort_values().head(N)`  
✅ **聚合计算**：`groupby().agg()`  
✅ **画折线图**：`plt.plot()`  
✅ **画柱状图**：`ax.bar()`  
✅ **双轴图**：`ax.twinx()`  
✅ **标注箭头**：`plt.annotate()`  
✅ **自定义图例**：`mpatches.Patch` + `Line2D`  
✅ **自动结论**：条件判断 + 打印分析  
✅ **导出Excel**：`pd.ExcelWriter` + `xlsxwriter`  

> **下一步建议**：把自己的数据替换进来，先跑通代码，再逐步修改颜色、标题、判断阈值，让报表真正属于你的业务场景。
