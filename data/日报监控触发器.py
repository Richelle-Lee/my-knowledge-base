#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
日报监控触发器
==============
逻辑：每隔3分钟检查一次
  - 3个数据文件夹里是否都存在当天的文件（文件修改时间是今天）
  - 当前时间是否 >= 11:00
  - 今天是否还没执行过
以上三个条件同时满足 → 执行日报脚本 → 记录已执行
任何一天都生效（包括周日），不区分星期几。
"""

import os
import sys
import time
import logging
import subprocess
from datetime import datetime, date
from pathlib import Path

# ══════════════════════════════════════════════════════════
# ★ 配置区 —— 根据实际情况修改
# ══════════════════════════════════════════════════════════

# 需要监控的3个数据文件夹（每个盘对应一个）
WATCH_FOLDERS = [
    r"D:\Afun_mx自动播报",
    r"D:\soluno自动播报",
    r"D:\wey7自动播报",
    r"D:\sol777自动播报",
    r"D:\Lucro自动播报",
    r"D:\3bet自动播报",
    r"D:\A7X自动播报",
]

# 每个文件夹里要找的文件名通配规则（匹配含今天日期的xlsx文件）
# 文件名示例：日报-大盘日报_20260527.xlsx
FILE_GLOB = "日报-大盘日报_*.xlsx"

# 日报 notebook 路径
NOTEBOOK_PATH = r"C:\Users\Administrator\Desktop\大盘日报_自动播报代码.ipynb"

# 执行日志文件路径
LOG_FILE = r"C:\Users\Administrator\Desktop\日报运行日志.txt"

# 今日已执行标记文件（每天执行后写入，防止重复运行）
DONE_FLAG_FILE = r"C:\Users\Administrator\Desktop\.日报已执行_标记.txt"

# 最早允许执行的时间（24小时制）
EXECUTE_HOUR   = 11
EXECUTE_MINUTE = 0

# 检查间隔（秒）
CHECK_INTERVAL = 180   # 3分钟

# jupyter 可执行路径（如果 jupyter 不在 PATH 里，填完整路径）
JUPYTER_EXE = r"C:\Users\Administrator\AppData\Local\Python\pythoncore-3.14-64\Scripts\jupyter.exe"

# notebook 执行超时（秒）
NB_TIMEOUT = 1200   # 20分钟，多个盘时间较长

# ══════════════════════════════════════════════════════════
# 日志初始化
# ══════════════════════════════════════════════════════════
Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════
# 核心判断函数
# ══════════════════════════════════════════════════════════

def today_str() -> str:
    """返回今天的日期字符串，格式 20260527"""
    return date.today().strftime("%Y%m%d")


def is_after_execute_time() -> bool:
    """当前时间是否已到或超过执行时间（默认11:00）"""
    now = datetime.now()
    return (now.hour, now.minute) >= (EXECUTE_HOUR, EXECUTE_MINUTE)


def folder_has_todays_file(folder: str) -> tuple[bool, str]:
    """
    检查文件夹里是否存在当天的数据文件。
    判断方式：文件名包含今天日期（YYYYMMDD），且文件修改时间也是今天。
    返回 (是否存在, 找到的文件名或原因)
    """
    folder_path = Path(folder)
    if not folder_path.exists():
        return False, f"文件夹不存在: {folder}"

    today = today_str()
    today_date = date.today()

    for f in folder_path.glob(FILE_GLOB):
        # 方式1：文件名包含今天日期
        if today in f.name:
            return True, f.name
        # 方式2：文件修改时间是今天（兜底，防止文件名不含日期）
        mtime = date.fromtimestamp(f.stat().st_mtime)
        if mtime == today_date:
            return True, f.name

    return False, f"未找到今日文件（{today}）"


def all_folders_ready() -> tuple[bool, list[str]]:
    """检查所有监控文件夹是否都有今天的文件，返回(全部就绪, 详情列表)"""
    details = []
    all_ok = True
    for folder in WATCH_FOLDERS:
        ok, info = folder_has_todays_file(folder)
        status = "✅" if ok else "❌"
        details.append(f"  {status} {Path(folder).name}: {info}")
        if not ok:
            all_ok = False
    return all_ok, details


def already_ran_today() -> bool:
    """今天是否已经执行过"""
    flag = Path(DONE_FLAG_FILE)
    if not flag.exists():
        return False
    content = flag.read_text(encoding="utf-8").strip()
    return content == today_str()


def mark_done_today():
    """标记今天已执行"""
    Path(DONE_FLAG_FILE).write_text(today_str(), encoding="utf-8")


# ══════════════════════════════════════════════════════════
# 执行日报
# ══════════════════════════════════════════════════════════

def run_report() -> bool:
    """执行 notebook，返回是否成功"""
    log.info("=" * 50)
    log.info("🚀 开始执行日报脚本...")
    log.info(f"   Notebook: {NOTEBOOK_PATH}")

    cmd = [
        JUPYTER_EXE, "nbconvert",
        "--to", "notebook",
        "--execute",
        NOTEBOOK_PATH,
        "--inplace",
        f"--ExecutePreprocessor.timeout={NB_TIMEOUT}",
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=NB_TIMEOUT + 60,
        )
        if result.returncode == 0:
            log.info("✅ 日报执行成功！")
            if result.stdout.strip():
                log.info(f"输出：{result.stdout.strip()[:500]}")
            return True
        else:
            log.error(f"❌ 日报执行失败，返回码：{result.returncode}")
            if result.stderr.strip():
                log.error(f"错误信息：{result.stderr.strip()[:1000]}")
            return False
    except subprocess.TimeoutExpired:
        log.error(f"❌ 执行超时（>{NB_TIMEOUT}秒）")
        return False
    except FileNotFoundError:
        log.error(f"❌ 找不到 jupyter，请检查 JUPYTER_EXE 配置：{JUPYTER_EXE}")
        log.error("   尝试：pip install jupyter nbconvert")
        return False
    except Exception as e:
        log.error(f"❌ 执行异常：{e}")
        return False


# ══════════════════════════════════════════════════════════
# 主循环
# ══════════════════════════════════════════════════════════

def main():
    log.info("=" * 50)
    log.info("📡 日报监控触发器已启动")
    log.info(f"   监控文件夹：{len(WATCH_FOLDERS)} 个")
    for f in WATCH_FOLDERS:
        log.info(f"   - {f}")
    log.info(f"   执行时间条件：{EXECUTE_HOUR:02d}:{EXECUTE_MINUTE:02d} 之后")
    log.info(f"   检查间隔：{CHECK_INTERVAL} 秒")
    log.info("=" * 50)

    while True:
        now = datetime.now()
        weekday_name = ["周一","周二","周三","周四","周五","周六","周日"][now.weekday()]

        # ── 检查是否已执行过今天 ─────────────────────────
        if already_ran_today():
            log.debug(f"今日已执行，跳过。下次检查：{CHECK_INTERVAL}秒后")
            time.sleep(CHECK_INTERVAL)
            continue

        # ── 检查时间是否到11点 ───────────────────────────
        if not is_after_execute_time():
            wait_min = (EXECUTE_HOUR * 60 + EXECUTE_MINUTE) - (now.hour * 60 + now.minute)
            log.info(f"[{weekday_name} {now.strftime('%H:%M')}] 未到执行时间，"
                     f"距11:00还有约{wait_min}分钟")
            time.sleep(CHECK_INTERVAL)
            continue

        # ── 检查3个文件夹是否都有今天文件 ───────────────
        all_ready, details = all_folders_ready()
        log.info(f"[{weekday_name} {now.strftime('%H:%M')}] 文件检查结果：")
        for d in details:
            log.info(d)

        if not all_ready:
            log.info("  ⏳ 等待文件就绪，继续监控...")
            time.sleep(CHECK_INTERVAL)
            continue

        # ── 三个条件全满足，执行日报 ─────────────────────
        log.info(f"  ✅ 所有文件就绪，时间已过11点，开始执行日报！")
        success = run_report()

        if success:
            mark_done_today()
            log.info(f"  📌 已标记今日（{today_str()}）执行完成，今日不再重复运行")
        else:
            log.warning("  ⚠️  本次执行失败，3分钟后会重试")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.info("\n🛑 监控器已手动停止")

