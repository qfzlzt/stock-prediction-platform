from __future__ import annotations

from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

from .utils import clean_col, ensure_datetime


def _read_xlsx_fast(path: Path, max_empty_streak: int = 50) -> pd.DataFrame:
    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    it = ws.iter_rows(values_only=True)
    try:
        first = next(it)
    except StopIteration:
        first = None
    if first is None:
        wb.close()
        return pd.DataFrame()
    header_raw = [str(c) if c is not None else "" for c in first]
    last_nonempty = -1
    for i, h in enumerate(header_raw):
        if str(h).strip() != "":
            last_nonempty = i
    if last_nonempty < 0:
        wb.close()
        return pd.DataFrame()
    width = last_nonempty + 1
    header = header_raw[:width]
    rows = []
    empty_streak = 0
    for r in it:
        if r is None:
            empty_streak += 1
            if empty_streak >= max_empty_streak:
                break
            continue
        r = tuple(r[:width])
        if all(v is None or str(v).strip() == "" for v in r):
            empty_streak += 1
            if empty_streak >= max_empty_streak:
                break
            continue
        empty_streak = 0
        rows.append(r)
    wb.close()
    return pd.DataFrame(rows, columns=header)


def _resolve_data_file(base_dir: str | Path, file_name: str) -> Path:
    def _is_nonempty(fp: Path) -> bool:
        if not fp.exists():
            return False
        try:
            with open(fp, "rb") as f:
                head = f.read(16)
            return len(head) > 0
        except OSError:
            return False

    base = Path(base_dir).resolve()
    p = base / file_name
    if _is_nonempty(p):
        return p

    # Fallback: search nearby project folders for the same dataset file.
    search_roots = [base.parent]
    search_roots.extend(base.parents[:3])
    seen = set()
    for root in search_roots:
        if root in seen:
            continue
        seen.add(root)
        for cand in sorted(root.rglob(file_name)):
            if cand == p:
                continue
            if _is_nonempty(cand):
                return cand

    for cand in sorted(base.rglob(file_name)):
        if cand == p:
            continue
        if _is_nonempty(cand):
            return cand

    raise FileNotFoundError(f"Data file not found or empty: {p}")


def load_industry_map(base_dir: str | Path, industry_file: str) -> pd.DataFrame:
    p = _resolve_data_file(base_dir, industry_file)
    df = _read_xlsx_fast(p)
    df.columns = [clean_col(c) for c in df.columns]

    code_col = [c for c in df.columns if "证券代码" in c or c == "证券代码"]
    ind_col = [c for c in df.columns if "所属申万行业" in c]
    if not code_col or not ind_col:
        # fallback to original names
        raw = _read_xlsx_fast(p)
        code_col = [c for c in raw.columns if "证券代码" in str(c)][0]
        ind_col = [c for c in raw.columns if "所属申万行业" in str(c)][0]
        out = raw[[code_col, ind_col]].copy()
        out.columns = ["stock", "industry_l3"]
    else:
        out = df[[code_col[0], ind_col[0]]].copy()
        out.columns = ["stock", "industry_l3"]

    out["stock"] = out["stock"].astype(str).str.extract(r"(\d{6})")
    out["industry_l3"] = out["industry_l3"].astype(str)
    return out.dropna(subset=["stock"]).drop_duplicates("stock")


def load_market_index(base_dir: str | Path, market_file: str) -> pd.DataFrame:
    p = _resolve_data_file(base_dir, market_file)
    df = _read_xlsx_fast(p, max_empty_streak=30)
    if df.empty:
        raise ValueError(f"Market file is empty: {p}")
    rename_map = {c: clean_col(c) for c in df.columns}
    df = df.rename(columns=rename_map)
    # Market-file-specific alias normalization
    market_alias = {
        "float_mv": "mkt_float_mv",
        "turnover": "mkt_turnover",
        "流通换手率": "mkt_float_turnover",
        "平均市盈率": "mkt_pe_mean",
        "成交量": "mkt_volume",
        "成交金额": "mkt_amount",
        "挂牌数": "mkt_listed_count",
        "市价总值": "mkt_total_mv",
        "trade_date": "date",
    }
    for src, dst in market_alias.items():
        if src in df.columns and dst not in df.columns:
            df = df.rename(columns={src: dst})
    df = ensure_datetime(df, "date").sort_values("date")

    # Avoid name collisions with stock-level columns after merge.
    if "volume" in df.columns and "mkt_volume" not in df.columns:
        df = df.rename(columns={"volume": "mkt_volume"})
    if "amount" in df.columns and "mkt_amount" not in df.columns:
        df = df.rename(columns={"amount": "mkt_amount"})

    # Determine anchor market level series for regime/return features.
    anchor_col = None
    for c in ["star_close_total_w", "star_close_float_w", "star_close_mean", "mkt_total_mv", "mkt_float_mv"]:
        if c in df.columns:
            anchor_col = c
            break
    if anchor_col is None:
        cand = [c for c in df.columns if c != "date" and pd.api.types.is_numeric_dtype(df[c])]
        if not cand:
            raise ValueError("No usable numeric market column found in market file.")
        anchor_col = cand[0]

    df["star_close_total_w"] = pd.to_numeric(df[anchor_col], errors="coerce")

    df["mkt_ret_1"] = df["star_close_total_w"].pct_change(1)
    df["mkt_ret_5"] = df["star_close_total_w"].pct_change(5)
    df["mkt_ret_20"] = df["star_close_total_w"].pct_change(20)
    df["mkt_vol_20"] = df["mkt_ret_1"].rolling(20).std()
    rolling_max = df["star_close_total_w"].rolling(60, min_periods=1).max()
    df["mkt_drawdown_60"] = df["star_close_total_w"] / rolling_max - 1.0

    # Keep all market numeric fields so model can learn board-level context.
    keep = ["date"] + [c for c in df.columns if c != "date" and pd.api.types.is_numeric_dtype(df[c])]
    return df[keep].copy()


def load_stock_panel(base_dir: str | Path, stock_glob: str) -> pd.DataFrame:
    base = Path(base_dir).resolve()
    files = sorted(base.glob(stock_glob))
    if not files:
        raise FileNotFoundError(f"No files matched: {base / stock_glob}")

    parts = []
    for fp in files:
        stock = fp.name[:6]
        try:
            df = _read_xlsx_fast(fp)
        except Exception:
            # Fallback to the same file name from nearby project folders.
            alt = None
            search_roots = [base.parent]
            search_roots.extend(base.parents[:3])
            seen = set()
            for root in search_roots:
                if root in seen:
                    continue
                seen.add(root)
                for cand in sorted(root.rglob(fp.name)):
                    if cand == fp:
                        continue
                    try:
                        df = _read_xlsx_fast(cand)
                        alt = cand
                        break
                    except Exception:
                        continue
                if alt is not None:
                    break
            if alt is None:
                for cand in sorted(base.rglob(fp.name)):
                    if cand == fp:
                        continue
                    try:
                        df = _read_xlsx_fast(cand)
                        alt = cand
                        break
                    except Exception:
                        continue
            if alt is None:
                raise
        df = df.rename(columns={c: clean_col(c) for c in df.columns})
        if "date" not in df.columns:
            raise ValueError(f"'日期' column missing in {fp.name}")
        df = ensure_datetime(df, "date")
        df["stock"] = stock

        # enforce common ohlcv aliases if still in Chinese
        cn_alias = {
            "收盘价": "close",
            "开盘价": "open",
            "最高价": "high",
            "最低价": "low",
            "成交量": "volume",
            "成交额": "amount",
        }
        for c_cn, c_en in cn_alias.items():
            if c_cn in df.columns and c_en not in df.columns:
                df = df.rename(columns={c_cn: c_en})

        parts.append(df)

    panel = pd.concat(parts, ignore_index=True)
    panel = panel.sort_values(["stock", "date"]).reset_index(drop=True)
    return panel
