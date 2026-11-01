"""Configuration from environment variables; no credentials are stored here."""
import os
from pathlib import Path
import pymysql.cursors

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_SRC_DIR = Path(os.environ.get("MODEL_SRC_DIR", PROJECT_ROOT / "model"))
ARTIFACTS_DIR = Path(os.environ.get("ARTIFACTS_DIR", MODEL_SRC_DIR / "outputs" / "artifacts"))
INDUSTRY_EXCEL = Path(os.environ.get("INDUSTRY_EXCEL", PROJECT_ROOT / "data" / "21公司行业分类.xlsx"))

def database_config():
    return {
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": int(os.environ.get("DB_PORT", "3306")),
        "user": os.environ.get("DB_USER", "root"),
        "password": os.environ["DB_PASSWORD"],
        "database": os.environ.get("DB_NAME", "stock"),
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
    }
