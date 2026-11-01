"""
launcher.py  —  AI 预测服务启动器
双击 start.bat 后由此脚本接管，处理所有启动逻辑。
"""
import subprocess
import sys
import os
import datetime

# 切换工作目录到脚本所在位置
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 50)
print("  Stock AI Prediction Service  (port 8083)")
print("=" * 50)
print()

# ── 1. 安装依赖 ──────────────────────────────────────
print("[1/3] Installing dependencies...")
pkgs = ["flask", "flask-cors", "pymysql", "pandas",
        "numpy", "lightgbm", "torch", "scikit-learn", "openpyxl"]
# Install dependencies explicitly with pip install -r requirements.txt.
print("      Done.\n")

# ── 2. 检查数据库 / 特征表 ───────────────────────────
print("[2/3] Checking database...")
try:
    import pymysql

    from settings import database_config
    options = database_config()
    options.pop("cursorclass", None)  # Launcher reads the result as a tuple.
    conn = pymysql.connect(**options)
    cur = conn.cursor()

    # 建表（如果不存在）
    from build_features import ensure_table
    ensure_table(conn)

    # 检查数据新鲜度
    cur.execute("SELECT MAX(trade_date) FROM model_input_features")
    row = cur.fetchone()
    conn.close()

    if not row or not row[0]:
        status = "EMPTY"
    else:
        diff = (datetime.date.today() - row[0]).days
        status = "STALE" if diff > 3 else "OK"

except Exception as e:
    status = f"ERROR: {e}"

print(f"      Status: {status}\n")

if status == "EMPTY":
    print("      First run — building features (a few minutes)...")
    from build_features import main as build_main
    build_main()
    print("      Build complete.\n")
elif status == "STALE":
    print("      Data stale — refreshing features...")
    from build_features import main as build_main
    build_main()
    print("      Refresh complete.\n")
elif status.startswith("ERROR"):
    print(f"      WARNING: {status}")
    print("      Service will start, but predictions may fail.\n")

# ── 3. 启动 Flask ────────────────────────────────────
print("[3/3] Starting Flask on http://localhost:8083 ...")
print()
print("=" * 50)
print("  Ready: http://localhost:8083")
print("  Press Ctrl+C to stop")
print("=" * 50)
print()

import app as flask_app
flask_app.app.run(host="0.0.0.0", port=8083, debug=False)
