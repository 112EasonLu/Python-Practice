# merged_data_and_plot.py
# 完整版 — 修正過的 merged script（Python 3.9+）
# 主要變更：
# - get_stock_name() 提前定義（避免未定義錯誤）
# - plot_technical_chart(..., save_plot=True) 可選是否輸出 PNG（預設保留舊行為）
# - plot_combined_chart(...)：標題改為 "XXXX 公司名稱 技術分析 & 三大法人籌碼報表（策略名）"
#   -> 右側前兩張子圖與左側對齊 (K + Volume)
#   -> 子圖上下緊貼（合併上下邊界，hspace=0，並隱藏相鄰 spines）
# - 呼叫 plot_combined_chart 時會傳入 strategy_name
#
# 請直接覆蓋你原本的 merged_data_and_plot.py 檔案（已保留你原來的流程 / 輸出）
# 注意：此檔會呼叫網路 (yfinance, fubon)，執行會需要網路與相依套件安裝


import os
import re
import time
from datetime import datetime, timedelta, date
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib import rcParams, font_manager
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import twstock
from functools import lru_cache
from mplfinance.original_flavor import candlestick_ohlc

# -------------------------
# Matplotlib CJK font setup
# -------------------------
def set_cjk_font(preferred=None, fonts_dir="fonts"):
    candidates = preferred or [
        "Microsoft JhengHei", "Microsoft JhengHei UI", "PMingLiU", "MingLiU",
        "PingFang TC", "Heiti TC", "Noto Sans CJK TC", "Taipei Sans TC Beta", "WenQuanYi Micro Hei",
    ]
    installed_names = [f.name for f in font_manager.fontManager.ttflist]
    chosen = None
    for c in candidates:
        if c in installed_names:
            chosen = c
            break
        if any(c in name for name in installed_names):
            chosen = next((name for name in installed_names if c in name), None)
            if chosen:
                break
    if not chosen and fonts_dir and os.path.isdir(fonts_dir):
        added = []
        for fname in os.listdir(fonts_dir):
            if fname.lower().endswith((".ttf", ".otf", ".ttc")):
                fpath = os.path.join(fonts_dir, fname)
                try:
                    font_manager.fontManager.addfont(fpath)
                    added.append(fpath)
                except Exception:
                    pass
        if added:
            installed_names = [f.name for f in font_manager.fontManager.ttflist]
            for c in candidates:
                if c in installed_names:
                    chosen = c
                    break
            if not chosen:
                try:
                    chosen = font_manager.FontProperties(fname=added[0]).get_name()
                except Exception:
                    chosen = None
    if chosen:
        rcParams["font.family"] = "sans-serif"
        rcParams["font.sans-serif"] = [chosen] + list(rcParams.get("font.sans-serif", []))
        print(f"✅ 已設定 Matplotlib 字型：{chosen}")
    else:
        print("⚠️ 未找到常見的繁中文字型；建議安裝或放置字型於專案 fonts/ 目錄（例如 Noto Sans CJK TC）。")
    rcParams["axes.unicode_minus"] = False

set_cjk_font()

# -------------------------
# util functions
# -------------------------
def _to_int_safe(x):
    if x is None:
        return 0
    s = str(x).strip()
    if s in ["", "-", "—", "–", "－"]:
        return 0
    s = s.replace(",", "")
    m = re.fullmatch(r"\((\d+)\)", s)
    if m:
        return -int(m.group(1))
    try:
        return int(float(s))
    except Exception:
        return 0

def _fmt_k(v, pos=None):
    try:
        return f"{int(round(v/1000.0))}K"
    except Exception:
        return str(v)

def _parse_one_date(text: str, fallback_year: int) -> date | None:
    if text is None:
        return None
    s = str(text).strip()
    if s == "":
        return None
    s = s.replace(".", "/").replace("-", "/")
    m = re.match(r"^\s*(\d{1,4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日\s*$", s)
    if m:
        y = int(m.group(1))
        mth = int(m.group(2))
        d = int(m.group(3))
        if y < 1000:
            y += 1911
        return date(y, mth, d)
    parts = s.split("/")
    if len(parts) == 3 and len(parts[0]) >= 1:
        try:
            y = int(parts[0])
            mth = int(parts[1])
            d = int(parts[2])
            if y < 1000:
                y += 1911
            return date(y, mth, d)
        except Exception:
            pass
    if len(parts) == 2:
        try:
            mth = int(parts[0])
            d = int(parts[1])
            y = int(fallback_year)
            return date(y, mth, d)
        except Exception:
            pass
    m = re.match(r"^\s*(\d{4})(\d{2})(\d{2})\s*$", s)
    if m:
        y = int(m.group(1))
        mth = int(m.group(2))
        d = int(m.group(3))
        try:
            return date(y, mth, d)
        except Exception:
            return None
    return None

def _parse_fubon_dates(series: pd.Series, end_date_str: str, debug_path: str | None = None) -> pd.Series:
    fallback_year = int(pd.to_datetime(end_date_str).year)
    parsed = series.astype(str).apply(lambda x: _parse_one_date(x, fallback_year))
    if parsed.isna().all() and debug_path:
        try:
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write("\n".join(series.astype(str).tolist()))
        except Exception:
            pass
    return parsed

def _make_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
        "Referer": "https://fubon-ebrokerdj.fbs.com.tw/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Upgrade-Insecure-Requests": "1",
    })
    retry = Retry(
        total=3, backoff_factor=0.6,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    try:
        s.get("https://fubon-ebrokerdj.fbs.com.tw/", timeout=20)
    except Exception:
        pass
    return s

# -------------------------
# stock name (提前定義)
# -------------------------
@lru_cache(maxsize=None)
def get_stock_name(stock_id: str) -> str:
    try:
        stock = twstock.codes.get(stock_id)
        if stock and getattr(stock, "name", None):
            return stock.name
    except Exception:
        pass
    return "未知公司"

# -------------------------
# 圖：技術指標 K 線圖（可選是否輸出 PNG）
# -------------------------
def plot_technical_chart(file_path, output_dir="plots", today_str_override=None, save_plot=True, days=60):
    """
    讀取單檔 qualified CSV，計算技術指標，回傳處理後 DataFrame（最近最多 days）。
    如果 save_plot=True，會輸出 technical png（保持原行為）。
    """
    try:
        fname = os.path.basename(file_path)
        stock_id = fname.split("_")[0]
        stock_name = get_stock_name(stock_id)

        df = pd.read_csv(file_path)
        df.columns = [c.strip().lower() for c in df.columns]
        rename_map = {
            "date": "Date", "open": "Open", "high": "High", "low": "Low", "close": "Close",
            "volume": "Volume", "capacity": "Volume", "成交量": "Volume"
        }
        df.rename(columns=rename_map, inplace=True)
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)

        df["Volume"] = df.get("Volume", pd.Series(0, index=df.index)).astype(float) / 1000.0
        for ma in [5, 10, 20, 60, 100]:
            df[f"MA{ma}"] = df["Close"].rolling(ma, min_periods=1).mean()
        df["BB_MID"] = df["Close"].rolling(20, min_periods=1).mean()
        df["BB_STD"] = df["Close"].rolling(20, min_periods=1).std(ddof=0)
        df["BB_UPPER"] = df["BB_MID"] + 2 * df["BB_STD"]
        df["BB_LOWER"] = df["BB_MID"] - 2 * df["BB_STD"]
        df["VOL_MA5"] = df["Volume"].rolling(5, min_periods=1).mean()
        df["VOL_MA20"] = df["Volume"].rolling(20, min_periods=1).mean()

        # KD
        low_min = df["Low"].rolling(9, min_periods=1).min()
        high_max = df["High"].rolling(9, min_periods=1).max()
        den = (high_max - low_min).replace(0, np.nan)
        rsv = (df["Close"] - low_min) / den * 100
        df["K"] = rsv.ewm(alpha=1/3, adjust=False).mean()
        df["D"] = df["K"].ewm(alpha=1/3, adjust=False).mean()

        # RSI
        delta = df["Close"].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.rolling(14, min_periods=1).mean()
        avg_loss = loss.rolling(14, min_periods=1).mean().replace(0, np.nan)
        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))
        df["RSI"] = df["RSI"].fillna(50)

        # MACD
        ema12 = df["Close"].ewm(span=12, adjust=False).mean()
        ema26 = df["Close"].ewm(span=26, adjust=False).mean()
        df["MACD"] = ema12 - ema26
        df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
        df["Hist"] = df["MACD"] - df["Signal"]

        if len(df) > days:
            df = df.tail(days).reset_index(drop=True)

        df = df.reset_index(drop=True)
        df["x"] = np.arange(len(df))

        # 若 save_plot=True，畫技術圖（與你原本行為一致）
        if save_plot:
            try:
                plt.rcParams.update({'font.size': 10})
                fig, (ax_candle, ax_vol, ax_kd, ax_rsi, ax_macd) = plt.subplots(
                    5, 1, figsize=(16, 14), sharex=True,
                    gridspec_kw={'height_ratios': [3, 1, 1, 1, 1]},
                    constrained_layout=False
                )
                #plt.subplots_adjust(hspace=0.03, top=0.96, bottom=0.06)
                plt.subplots_adjust(hspace=0, top=0.96, bottom=0.06)
                width = 0.6
                up_color, down_color = 'red', 'green'

                # K
                quotes = df[['x', 'Open', 'High', 'Low', 'Close']].values
                candlestick_ohlc(ax_candle, quotes, width=width, colorup=up_color, colordown=down_color, alpha=1.0)
                ma_colors = {5:'orange', 10:'gold', 20:'blue', 60:'purple', 100:'brown'}
                for ma, color in ma_colors.items():
                    if f"MA{ma}" in df.columns:
                        ax_candle.plot(df['x'], df[f"MA{ma}"], label=f"MA{ma}", color=color)
                if 'BB_UPPER' in df.columns:
                    ax_candle.plot(df['x'], df['BB_UPPER'], color='cyan', linestyle='--', linewidth=0.9)
                    ax_candle.plot(df['x'], df['BB_LOWER'], color='cyan', linestyle='--', linewidth=0.9)
                ax_candle.set_ylabel("Price")
                ax_candle.set_title(f"{stock_id} {stock_name} 技術分析圖", pad=5)
                ax_candle.legend(loc='upper left', fontsize=8)

                last = df.iloc[-1]
                txt_price = (
                    f"Open:{last['Open']:.2f}  High:{last['High']:.2f}  "
                    f"Low:{last['Low']:.2f}  Close:{last['Close']:.2f}\n"
                    f"MA5:{last.get('MA5', np.nan):.2f}  MA10:{last.get('MA10', np.nan):.2f}  MA20:{last.get('MA20', np.nan):.2f}\n"
                    f"BB_UPPER:{last.get('BB_UPPER', np.nan):.2f}  BB_LOWER:{last.get('BB_LOWER', np.nan):.2f}"
                )
                ax_candle.text(0.99, 0.98, txt_price, transform=ax_candle.transAxes,
                               fontsize=9, color='black', ha='right', va='top', clip_on=False, zorder=100)

                # Volume
                colors_vol = np.where(df["Close"] >= df["Open"], up_color, down_color)
                ax_vol.bar(df['x'], df['Volume'], color=colors_vol, width=width)
                if 'VOL_MA5' in df.columns:
                    ax_vol.plot(df['x'], df['VOL_MA5'], color='blue', label='VOL_MA5')
                if 'VOL_MA20' in df.columns:
                    ax_vol.plot(df['x'], df['VOL_MA20'], color='orange', label='VOL_MA20')
                ax_vol.set_ylabel("Volume (張)")
                ax_vol.legend(loc='upper left', fontsize=8)
                ax_vol.text(0.99, 0.98,
                            f"Vol:{last.get('Volume', np.nan):.1f}  VOL_MA5:{last.get('VOL_MA5', np.nan):.1f}  VOL_MA20:{last.get('VOL_MA20', np.nan):.1f}",
                            transform=ax_vol.transAxes, fontsize=9, color='black', ha='right', va='top')

                # KD
                ax_kd.plot(df['x'], df['K'], color='orange', label='K')
                ax_kd.plot(df['x'], df['D'], color='blue', label='D')
                ax_kd.axhline(80, color='gray', linestyle='--', linewidth=0.8)
                ax_kd.axhline(20, color='gray', linestyle='--', linewidth=0.8)
                ax_kd.set_ylim(0, 100)
                ax_kd.legend(loc='upper left', fontsize=8)
                ax_kd.text(0.99, 0.98, f"K:{last.get('K', np.nan):.1f}  D:{last.get('D', np.nan):.1f}",
                           transform=ax_kd.transAxes, fontsize=9, color='black', ha='right', va='top', clip_on=False, zorder=100)

                # RSI
                ax_rsi.plot(df['x'], df['RSI'], color='magenta', label='RSI(14)')
                ax_rsi.axhline(70, color='gray', linestyle='--', linewidth=0.8)
                ax_rsi.axhline(30, color='gray', linestyle='--', linewidth=0.8)
                ax_rsi.set_ylim(0, 100)
                ax_rsi.legend(loc='upper left', fontsize=8)
                ax_rsi.text(0.99, 0.98, f"RSI:{last.get('RSI', np.nan):.1f}",
                            transform=ax_rsi.transAxes, fontsize=9, color='black', ha='right', va='top', clip_on=False, zorder=100)

                # MACD
                hist_colors = np.where(df["Hist"] >= 0, up_color, down_color)
                ax_macd.bar(df['x'], df['Hist'], color=hist_colors, width=width)
                ax_macd.plot(df['x'], df['MACD'], color='blue', label='MACD')
                ax_macd.plot(df['x'], df['Signal'], color='orange', label='Signal')
                ax_macd.legend(loc='upper left', fontsize=8)
                ax_macd.text(0.99, 0.98,
                             f"MACD:{last.get('MACD', np.nan):.2f}  Signal:{last.get('Signal', np.nan):.2f}",
                             transform=ax_macd.transAxes, fontsize=9, color='black', ha='right', va='top', clip_on=False, zorder=100)

                step = max(1, len(df)//10)
                xticks = df["x"][::step]
                xlabels = df["Date"].dt.strftime("%m-%d")
                xlabels = xlabels.tolist()[::step]
                for ax in [ax_candle, ax_vol, ax_kd, ax_rsi, ax_macd]:
                    ax.set_xticks(xticks)
                    ax.set_xticklabels(xlabels, rotation=45, ha='right')

                os.makedirs(output_dir, exist_ok=True)
                today_str_local = today_str_override or datetime.now().strftime("%Y%m%d")
                strategy_name = "Unknown"
                for s in ["blackinverse", "iamfly", "pre_fly"]:
                    if s in fname.lower():
                        strategy_name = s.capitalize()
                output_file = os.path.join(output_dir, f"{today_str_local}_{strategy_name}_{stock_id}_technical.png")
                plt.savefig(output_file, dpi=200, bbox_inches='tight')
                plt.close(fig)
                print(f"✅ {stock_id} {stock_name} 圖完成 → {output_file}")
            except Exception as e:
                print(f"❌ {file_path} 畫技術圖發生錯誤：{e}")
                try:
                    plt.close()
                except Exception:
                    pass

        return df

    except Exception as e:
        print(f"❌ {file_path} 發生錯誤：{e}")
        return None

# -------------------------
# Fubon 擷取
# -------------------------
def fetch_fubon_institutional(stock_id, start_date, end_date, market_hint="auto", timeout=20, debug_dir=None):
    bases_twse = [
        "https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcl/zcl.djhtm",
        "https://fubon-ebrokerdj.fbs.com.tw/z/zc/zcl2/zcl2.djhtm",
    ]
    bases_otc = [
        "https://fubon-ebrokerdj.fbs.com.tw/z/zg/zcl/zcl.djhtm",
        "https://fubon-ebrokerdj.fbs.com.tw/z/zg/zcl2/zcl2.djhtm",
    ]
    if market_hint == "twse":
        bases = bases_twse + bases_otc
    elif market_hint == "otc":
        bases = bases_otc + bases_twse
    else:
        bases = bases_twse + bases_otc

    sess = _make_session()
    last_error = None

    for base in bases:
        try:
            params = {"a": stock_id, "c": start_date, "d": end_date}
            resp = sess.get(base, params=params, timeout=timeout)
            resp.raise_for_status()
            enc = (resp.encoding or "").lower()
            if "big5" in enc:
                resp.encoding = "big5"
            else:
                try:
                    ae = (resp.apparent_encoding or "").lower()
                except Exception:
                    ae = ""
                resp.encoding = "big5" if "big5" in ae else "utf-8"
            html = resp.text
            soup = BeautifulSoup(html, "lxml")
            def norm_text(t):
                return re.sub(r"\s+", " ", t).strip()
            menu_rows = soup.find_all("tr", id="oScrollMenu")
            if len(menu_rows) < 2:
                last_error = f"{stock_id}：{base} 表頭結構不符"
                if debug_dir:
                    os.makedirs(debug_dir, exist_ok=True)
                    with open(os.path.join(debug_dir, f"debug_{stock_id}_headfail.html"), "w", encoding=resp.encoding) as f:
                        f.write(html)
                continue
            header_group_row = menu_rows[0]
            header_cols_row = menu_rows[1]
            group_cells = header_group_row.find_all(["td", "th"])
            groups = []
            for cell in group_cells:
                gname = norm_text(cell.get_text())
                colspan = int(cell.get("colspan", "1"))
                if not gname:
                    groups.extend([""] * colspan)
                else:
                    groups.extend([gname] * colspan)
            field_cells = header_cols_row.find_all(["td", "th"])
            fields = [norm_text(c.get_text()) for c in field_cells]
            if len(groups) != len(fields):
                if len(groups) < len(fields):
                    groups += [""] * (len(fields) - len(groups))
                else:
                    groups = groups[:len(fields)]
            columns = []
            for g, f in zip(groups, fields):
                columns.append(f"{g}_{f}" if g and f else f)
            data_table = header_cols_row.find_parent("table")
            rows = []
            for tr in data_table.find_all("tr"):
                if tr is header_group_row or tr is header_cols_row:
                    continue
                if tr.get("id") == "oScrollFoot":
                    break
                tds = tr.find_all("td")
                if len(tds) != len(columns):
                    continue
                row = [norm_text(td.get_text()) for td in tds]
                if row and row[0] == "合計買賣超":
                    continue
                rows.append(row)
            if not rows:
                last_error = f"{stock_id}：{base} 無資料列"
                if debug_dir:
                    os.makedirs(debug_dir, exist_ok=True)
                    with open(os.path.join(debug_dir, f"debug_{stock_id}_nodata.html"), "w", encoding=resp.encoding) as f:
                        f.write(html)
                continue
            df_raw = pd.DataFrame(rows, columns=columns)
            cols = list(df_raw.columns)
            def pick(patterns_include, patterns_exclude=None):
                patterns_exclude = patterns_exclude or []
                cand = []
                for c in cols:
                    ok = all(p in c for p in patterns_include)
                    bad = any(p in c for p in patterns_exclude)
                    if ok and not bad:
                        cand.append(c)
                return cand
            col_date_candidates = [c for c in cols if "日期" in c or c.lower() == "date" or c == "日期"]
            col_date = col_date_candidates[0] if col_date_candidates else None
            col_fn = next(iter(pick(["買賣超", "外資"])), None)
            col_tn = next(iter(pick(["買賣超", "投信"])), None)
            cand_dn = pick(["買賣超", "自營商"])
            col_dn = next((c for c in cand_dn if ("自行" not in c and "避險" not in c)), None)
            dn_self = next((c for c in cand_dn if "自行" in c), None)
            dn_hedge = next((c for c in cand_dn if "避險" in c), None)
            col_fh = next((c for c in pick(["估計", "外資"], ["比重", "%"]) if "持股" in c), None)
            col_th = next((c for c in pick(["估計", "投信"], ["比重", "%"]) if "持股" in c), None)
            col_dh = next((c for c in pick(["估計", "自營商"], ["比重", "%"]) if "持股" in c), None)
            needed_any = [col_date, col_fn, col_tn, (col_dn or (dn_self and dn_hedge)), col_fh, col_th, col_dh]
            if any(x is None for x in needed_any):
                if debug_dir:
                    os.makedirs(debug_dir, exist_ok=True)
                    with open(os.path.join(debug_dir, f"debug_{stock_id}_columns.txt"), "w", encoding="utf-8") as f:
                        f.write("\n".join(cols))
                    with open(os.path.join(debug_dir, f"debug_{stock_id}_columns.html"), "w", encoding=resp.encoding) as f:
                        f.write(html)
                last_error = f"{stock_id}：{base} 欄位對應失敗"
                continue
            debug_dates_path = os.path.join(debug_dir, f"debug_{stock_id}_raw_dates.txt") if debug_dir else None
            parsed_dates = _parse_fubon_dates(df_raw[col_date], end_date, debug_path=debug_dates_path)
            df = pd.DataFrame({
                "date": parsed_dates,
                "foreign_net": df_raw[col_fn].apply(_to_int_safe),
                "trust_net":   df_raw[col_tn].apply(_to_int_safe),
                "foreign_hold": df_raw[col_fh].apply(_to_int_safe),
                "trust_hold":   df_raw[col_th].apply(_to_int_safe),
                "dealer_hold":  df_raw[col_dh].apply(_to_int_safe),
            })
            if col_dn:
                df["dealer_net"] = df_raw[col_dn].apply(_to_int_safe)
            else:
                df["dealer_net"] = df_raw[dn_self].apply(_to_int_safe) + df_raw[dn_hedge].apply(_to_int_safe)
            df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
            if df.empty:
                last_error = f"{stock_id}：{base} 解析後為空（日期解析失敗或資料全為空）"
                if debug_dir:
                    with open(os.path.join(debug_dir, f"debug_{stock_id}_parse_empty.txt"), "w", encoding="utf-8") as f:
                        f.write(f"columns:\n" + "\n".join(cols) + "\n\n")
                        f.write("raw dates:\n" + "\n".join(df_raw[col_date].astype(str).tolist()))
                continue
            return df
        except Exception as e:
            last_error = f"{stock_id}：{base} 例外 {e}"
            continue
    if last_error:
        print(last_error)
    return None

# -------------------------
# 三面板法人圖（保留）
# -------------------------
def plot_fubon_three_panels(df, sid, out_png):
    if df is None or df.empty:
        return
    df60 = df.tail(60).copy()
    dates = [d.strftime("%m/%d") for d in df60["date"]]
    color_fore_line = "#ff00ff"
    color_trust_line = "#4caf50"
    color_dealer_line = "#ff4081"
    color_pos_bar = "#2e7d32"
    color_neg_bar = "#c62828"
    fig, axes = plt.subplots(3, 1, figsize=(14, 7.5), sharex=True, gridspec_kw={"height_ratios": [1,1,1]})
    fig.suptitle(f"{sid} - 三大法人估計持股與買賣超（近 60 日）", fontsize=14, y=0.98)
    panels = [
        ("外資", "foreign_hold", "foreign_net", color_fore_line),
        ("投信", "trust_hold", "trust_net",   color_trust_line),
        ("自營商", "dealer_hold", "dealer_net", color_dealer_line),
    ]
    for ax, (label, hold_col, net_col, line_color) in zip(axes, panels):
        ax.plot(dates, df60[hold_col].values, color=line_color, linewidth=2.0, label=f"{label}持股")
        ax.set_ylabel("持股(張)", color=line_color)
        ax.tick_params(axis="y", labelcolor=line_color)
        ax2 = ax.twinx()
        net_vals = df60[net_col].values
        bar_colors = [color_pos_bar if v >= 0 else color_neg_bar for v in net_vals]
        ax2.bar(dates, net_vals, color=bar_colors, alpha=0.6, label=f"{label}買賣超")
        ax2.set_ylabel("買賣超(張)")
        ax2.yaxis.set_major_formatter(FuncFormatter(_fmt_k))
        max_abs_net = int(max(1000, max(abs(net_vals.max()), abs(net_vals.min()))))
        pad = max(1000, int(max_abs_net * 0.15))
        ax2.set_ylim(-max_abs_net - pad, max_abs_net + pad)
        last_d = df60["date"].iloc[-1].strftime("%m/%d")
        last_hold = int(df60[hold_col].iloc[-1])
        last_net = int(df60[net_col].iloc[-1])
        text_color = color_pos_bar if last_net >= 0 else color_neg_bar
        ax.text(0.01, 0.02,
                f"{last_d}  {last_hold:,}張（{label}持股）  {last_net:+,}張（{label}買賣超）",
                transform=ax.transAxes, fontsize=10, color=text_color, ha="left", va="bottom")
        ax.grid(True, axis="y", linestyle="--", alpha=0.25)
        ax2.grid(False)
    step = 5
    plt.xticks(range(0, len(dates), step), [dates[i] for i in range(0, len(dates), step)], rotation=45)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(out_png, dpi=120)
    plt.close(fig)

# -------------------------
# 合併圖：技術面 + 三大法人（完整）
# -------------------------
def plot_combined_chart(df_iv, tech_csv_path, sid, strategy_name, out_png, days=60, today_str_override=None):
    """
    Robust combined chart:
      - align df_tech and df_iv on a common Date index (intersection preferred)
      - forward-fill / fillna to avoid misaligned plotting
      - right-top two plots mirror left-top K and Volume
      - remove vertical gaps between subplots
    """
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    from mplfinance.original_flavor import candlestick_ohlc
    from matplotlib.ticker import FuncFormatter

    fig = None
    try:
        # --- 讀技術面（若有） ---
        df_tech = None
        if tech_csv_path and os.path.exists(tech_csv_path):
            # reuse plot_technical_chart for calculations but without saving plot
            df_tech = plot_technical_chart(tech_csv_path, output_dir=os.path.join(os.path.dirname(tech_csv_path), "..", "plot"), save_plot=False, days=days)
        # df_iv 來自 fetch_fubon_institutional，欄位預期包含 'date'

        # copy/normalize
        df_right = df_iv.copy() if (df_iv is not None and not df_iv.empty) else None

        # --- Robust date-column detection & normalization ---
        def _ensure_datecol(df, desired_name="Date"):
            if df is None:
                return None
            df = df.copy()
            # find column whose name lower() == 'date'
            date_col = next((c for c in df.columns if c.lower() == "date"), None)
            if date_col is None:
                return df  # nothing to do
            df[desired_name] = pd.to_datetime(df[date_col])
            return df

        df_tech = _ensure_datecol(df_tech, "Date")
        df_right = _ensure_datecol(df_right, "Date")

        # --- Align indices: choose intersection of dates if possible, else union ---
        common_index = None
        if (df_tech is not None) and (df_right is not None):
            idx_tech = pd.DatetimeIndex(df_tech["Date"].dropna().unique())
            idx_right = pd.DatetimeIndex(df_right["Date"].dropna().unique())
            inter = idx_tech.intersection(idx_right)
            if len(inter) >= max(3, min(len(idx_tech), len(idx_right)) // 4):  # prefer intersection if reasonable
                common_index = inter.sort_values()
            else:
                # if intersection too small, fallback to intersection if non-empty else union
                if len(inter) > 0:
                    common_index = inter.sort_values()
                else:
                    common_index = idx_tech.union(idx_right).sort_values()
        elif df_tech is not None:
            common_index = pd.DatetimeIndex(df_tech["Date"].dropna().unique()).sort_values()
        elif df_right is not None:
            common_index = pd.DatetimeIndex(df_right["Date"].dropna().unique()).sort_values()

        # If we have a common index, reindex both frames to it (so x axis lengths match)
        if common_index is not None and len(common_index) > 0:
            if df_tech is not None:
                df_tech = df_tech.set_index("Date").reindex(common_index).sort_index()
                # forward-fill sensible columns, then fill remaining with 0
                df_tech = df_tech.ffill().fillna(0).reset_index().rename(columns={"index": "Date"})
            if df_right is not None:
                df_right = df_right.set_index("Date").reindex(common_index).sort_index()
                # holdings likely cumulative -> ffill, net flows -> fill 0
                df_right = df_right.ffill().fillna(0).reset_index().rename(columns={"index": "Date"})
        else:
            # if no dates at all, keep originals (plots will show placeholders)
            pass

        # --- Prepare plotting canvas ---
        plt.rcParams.update({'font.size': 10})
        fig = plt.figure(figsize=(20, 10))
        gs = fig.add_gridspec(nrows=5, ncols=2, height_ratios=[3,1,1,1,1], width_ratios=[1,1],
                              hspace=0.0, wspace=0.18)  # hspace=0 to eliminate vertical gaps

        # Title
        stock_name = get_stock_name(sid)
        fig.suptitle(f"{sid} {stock_name} 技術分析 & 三大法人籌碼報表（{strategy_name}）", fontsize=15, y=0.985)

        # Left axes (technical)
        ax_left_k    = fig.add_subplot(gs[0,0])
        ax_left_vol  = fig.add_subplot(gs[1,0], sharex=ax_left_k)
        ax_left_kd   = fig.add_subplot(gs[2,0], sharex=ax_left_k)
        ax_left_rsi  = fig.add_subplot(gs[3,0], sharex=ax_left_k)
        ax_left_macd = fig.add_subplot(gs[4,0], sharex=ax_left_k)

        # Right axes (K, Vol mirror left; then foreign/trust/dealer)
        ax_right_k    = fig.add_subplot(gs[0,1], sharex=ax_left_k)
        ax_right_vol  = fig.add_subplot(gs[1,1], sharex=ax_left_k)
        ax_right_fore = fig.add_subplot(gs[2,1], sharex=ax_left_k)
        ax_right_trust= fig.add_subplot(gs[3,1], sharex=ax_left_k)
        ax_right_dealer=fig.add_subplot(gs[4,1], sharex=ax_left_k)

        up_color, down_color = 'red', 'green'

        # Helper to visually merge adjacent axes
        def _merge_neighbors(ax_top, ax_bottom):
            try:
                ax_top.spines['bottom'].set_visible(False)
                ax_bottom.spines['top'].set_visible(False)
                plt.setp(ax_top.get_xticklabels(), visible=False)
            except Exception:
                pass

        # ----- LEFT: technical plotting (if available) -----
        if df_tech is not None and not df_tech.empty:
            df = df_tech.copy().reset_index(drop=True)
            df['x'] = np.arange(len(df))

            # candlestick
            try:
                quotes = df[['x', 'Open', 'High', 'Low', 'Close']].values
                candlestick_ohlc(ax_left_k, quotes, width=0.6, colorup=up_color, colordown=down_color, alpha=1.0)
            except Exception:
                ax_left_k.plot(df['x'], df['Close'], label='Close')

            for ma in [5,10,20,60,100]:
                col = f"MA{ma}"
                if col in df.columns:
                    ax_left_k.plot(df['x'], df[col], label=col)
            ax_left_k.set_ylabel("Price")
            ax_left_k.legend(loc='upper left', fontsize=8)

            # volume
            colors_vol = np.where(df["Close"] >= df["Open"], up_color, down_color)
            ax_left_vol.bar(df['x'], df['Volume'], color=colors_vol, width=0.6)
            if 'VOL_MA5' in df.columns:
                ax_left_vol.plot(df['x'], df['VOL_MA5'], label='VOL_MA5')
            if 'VOL_MA20' in df.columns:
                ax_left_vol.plot(df['x'], df['VOL_MA20'], label='VOL_MA20')
            ax_left_vol.set_ylabel("Volume (k)")
            ax_left_vol.legend(loc='upper left', fontsize=8)

            # KD / RSI / MACD (guard column existence)
            if "K" in df.columns and "D" in df.columns:
                ax_left_kd.plot(df['x'], df['K'], label='K')
                ax_left_kd.plot(df['x'], df['D'], label='D')
                ax_left_kd.axhline(80, linestyle='--', linewidth=0.8)
                ax_left_kd.axhline(20, linestyle='--', linewidth=0.8)
                ax_left_kd.set_ylim(0, 100)
                ax_left_kd.legend(loc='upper left', fontsize=8)
            if "RSI" in df.columns:
                ax_left_rsi.plot(df['x'], df['RSI'], label='RSI(14)')
                ax_left_rsi.axhline(70, linestyle='--', linewidth=0.8)
                ax_left_rsi.axhline(30, linestyle='--', linewidth=0.8)
                ax_left_rsi.set_ylim(0, 100)
                ax_left_rsi.legend(loc='upper left', fontsize=8)
            if "Hist" in df.columns:
                ax_left_macd.bar(df['x'], df['Hist'], width=0.6, color=np.where(df['Hist']>=0, up_color, down_color))
            if "MACD" in df.columns:
                ax_left_macd.plot(df['x'], df['MACD'], label='MACD')
            if "Signal" in df.columns:
                ax_left_macd.plot(df['x'], df['Signal'], label='Signal')
            ax_left_macd.legend(loc='upper left', fontsize=8)

            # x ticks only on bottom-most left axis
            step = max(1, len(df)//10)
            xticks = df['x'][::step]
            xlabels = df['Date'].dt.strftime("%m-%d").tolist()[::step]
            for a in [ax_left_k, ax_left_vol, ax_left_kd, ax_left_rsi, ax_left_macd]:
                a.set_xticks(xticks)
            ax_left_macd.set_xticklabels(xlabels, rotation=45, ha='right')

            # merge left vertical neighbors
            _merge_neighbors(ax_left_k, ax_left_vol)
            _merge_neighbors(ax_left_vol, ax_left_kd)
            _merge_neighbors(ax_left_kd, ax_left_rsi)
            _merge_neighbors(ax_left_rsi, ax_left_macd)
        else:
            ax_left_k.text(0.5, 0.5, "No technical CSV found", ha='center', va='center', transform=ax_left_k.transAxes)
            for a in [ax_left_vol, ax_left_kd, ax_left_rsi, ax_left_macd]:
                a.set_visible(False)

        # ----- RIGHT: K & Vol mirror left top (use df_tech if present) -----
        if df_tech is not None and not df_tech.empty:
            dfR = df_tech.copy().reset_index(drop=True)
            dfR['x'] = np.arange(len(dfR))
            try:
                quotesR = dfR[['x','Open','High','Low','Close']].values
                candlestick_ohlc(ax_right_k, quotesR, width=0.6, colorup=up_color, colordown=down_color, alpha=1.0)
            except Exception:
                ax_right_k.plot(dfR['x'], dfR['Close'], label='Close')
            ax_right_k.set_title("K線 (技術資料)")

            colors_volR = np.where(dfR["Close"] >= dfR["Open"], up_color, down_color)
            ax_right_vol.bar(dfR['x'], dfR['Volume'], color=colors_volR, width=0.6)
            ax_right_vol.set_ylabel("Vol (k)")

            # merge right vertical neighbors
            _merge_neighbors(ax_right_k, ax_right_vol)
            _merge_neighbors(ax_right_vol, ax_right_fore)
            _merge_neighbors(ax_right_fore, ax_right_trust)
            _merge_neighbors(ax_right_trust, ax_right_dealer)
        else:
            ax_right_k.text(0.5, 0.5, "No K data", ha='center', va='center', transform=ax_right_k.transAxes)
            ax_right_vol.set_visible(False)

        # ----- RIGHT: 三大法人 panels (using df_right) -----
        if df_right is not None and not df_right.empty:
            # Ensure x index matches earlier x if df_tech exists; else use simple integer index
            if (df_tech is not None) and (df_tech is not None and not df_tech.empty):
                # use length of df_tech for x axis so they align visually
                x_idx = np.arange(len(df_tech))
                dates = df_tech["Date"].dt.strftime("%m/%d").tolist()
                # try to map df_right rows to df_tech positions by Date (they have same common_index)
                # we already reindexed df_right to common_index earlier so their indices align
                # prepare arrays by matching index
                try:
                    arr_fore_hold = df_right.get("foreign_hold", pd.Series(0, index=df_right.index)).values
                    arr_fore_net  = df_right.get("foreign_net", pd.Series(0, index=df_right.index)).values
                    arr_trust_hold= df_right.get("trust_hold", pd.Series(0, index=df_right.index)).values
                    arr_trust_net = df_right.get("trust_net", pd.Series(0, index=df_right.index)).values
                    arr_dealer_hold = df_right.get("dealer_hold", pd.Series(0, index=df_right.index)).values
                    arr_dealer_net  = df_right.get("dealer_net", pd.Series(0, index=df_right.index)).values
                except Exception:
                    # fallback: length mismatch -> pad/truncate
                    l = len(x_idx)
                    def _pad(a):
                        a = np.asarray(a)
                        if a.size < l:
                            return np.pad(a, (l-a.size, 0), 'constant', constant_values=0)
                        return a[-l:]
                    arr_fore_hold = _pad(df_right.get("foreign_hold", []))
                    arr_fore_net  = _pad(df_right.get("foreign_net", []))
                    arr_trust_hold= _pad(df_right.get("trust_hold", []))
                    arr_trust_net = _pad(df_right.get("trust_net", []))
                    arr_dealer_hold = _pad(df_right.get("dealer_hold", []))
                    arr_dealer_net  = _pad(df_right.get("dealer_net", []))

                # plot external panels
                if len(arr_fore_hold) >= len(x_idx):
                    ax_right_fore.plot(x_idx, arr_fore_hold, linewidth=2.0, label="外資持股")
                    ax_right_fore.set_ylabel("持股(張)")
                if len(arr_fore_net) >= len(x_idx):
                    bars = arr_fore_net
                    ax_fore2 = ax_right_fore.twinx()
                    bar_colors = ["#2e7d32" if v>=0 else "#c62828" for v in bars]
                    ax_fore2.bar(x_idx, bars, color=bar_colors, alpha=0.6)
                    ax_fore2.yaxis.set_major_formatter(FuncFormatter(_fmt_k))
                    max_abs = max(1000, int(max(abs(bars.max()), abs(bars.min()))))
                    ax_fore2.set_ylim(-max_abs * 1.15, max_abs * 1.15)
                    last_hold = int(arr_fore_hold[-1]) if len(arr_fore_hold)>0 else 0
                    last_net  = int(arr_fore_net[-1]) if len(arr_fore_net)>0 else 0
                    txt = f"{(df_tech['Date'].iloc[-1]).strftime('%m/%d')}  {last_hold:,}張（外資持股）  {last_net:+,}張"
                    ax_right_fore.text(0.01, 0.02, txt, transform=ax_right_fore.transAxes,
                                       fontsize=9, color=("#2e7d32" if last_net>=0 else "#c62828"),
                                       ha="left", va="bottom", clip_on=False, zorder=100)

                if len(arr_trust_hold) >= len(x_idx):
                    ax_right_trust.plot(x_idx, arr_trust_hold, linewidth=2.0, label="投信持股")
                    ax_right_trust.set_ylabel("持股(張)")
                if len(arr_trust_net) >= len(x_idx):
                    bars = arr_trust_net
                    ax_trust2 = ax_right_trust.twinx()
                    bar_colors = ["#2e7d32" if v>=0 else "#c62828" for v in bars]
                    ax_trust2.bar(x_idx, bars, color=bar_colors, alpha=0.6)
                    ax_trust2.yaxis.set_major_formatter(FuncFormatter(_fmt_k))
                    max_abs = max(1000, int(max(abs(bars.max()), abs(bars.min()))))
                    ax_trust2.set_ylim(-max_abs * 1.15, max_abs * 1.15)
                    last_hold = int(arr_trust_hold[-1]) if len(arr_trust_hold)>0 else 0
                    last_net  = int(arr_trust_net[-1]) if len(arr_trust_net)>0 else 0
                    txt = f"{(df_tech['Date'].iloc[-1]).strftime('%m/%d')}  {last_hold:,}張（投信持股）  {last_net:+,}張"
                    ax_right_trust.text(0.01, 0.02, txt, transform=ax_right_trust.transAxes,
                                        fontsize=9, color=("#2e7d32" if last_net>=0 else "#c62828"),
                                        ha="left", va="bottom", clip_on=False, zorder=100)

                if len(arr_dealer_hold) >= len(x_idx):
                    ax_right_dealer.plot(x_idx, arr_dealer_hold, linewidth=2.0, label="自營商持股")
                    ax_right_dealer.set_ylabel("持股(張)")
                if len(arr_dealer_net) >= len(x_idx):
                    bars = arr_dealer_net
                    ax_dealer2 = ax_right_dealer.twinx()
                    bar_colors = ["#2e7d32" if v>=0 else "#c62828" for v in bars]
                    ax_dealer2.bar(x_idx, bars, color=bar_colors, alpha=0.6)
                    ax_dealer2.yaxis.set_major_formatter(FuncFormatter(_fmt_k))
                    max_abs = max(1000, int(max(abs(bars.max()), abs(bars.min()))))
                    ax_dealer2.set_ylim(-max_abs * 1.15, max_abs * 1.15)
                    last_hold = int(arr_dealer_hold[-1]) if len(arr_dealer_hold)>0 else 0
                    last_net  = int(arr_dealer_net[-1]) if len(arr_dealer_net)>0 else 0
                    txt = f"{(df_tech['Date'].iloc[-1]).strftime('%m/%d')}  {last_hold:,}張（自營商持股）  {last_net:+,}張"
                    ax_right_dealer.text(0.01, 0.02, txt, transform=ax_right_dealer.transAxes,
                                         fontsize=9, color=("#2e7d32" if last_net>=0 else "#c62828"),
                                         ha="left", va="bottom", clip_on=False, zorder=100)

                # set x ticks on right axes to same positions
                stepR = max(1, len(x_idx)//10)
                xticksR = x_idx[::stepR]
                xlabelsR = dates[::stepR]
                for a in [ax_right_k, ax_right_vol, ax_right_fore, ax_right_trust, ax_right_dealer]:
                    a.set_xticks(xticksR)
                ax_right_dealer.set_xticklabels(xlabelsR, rotation=45, ha='right')

            else:
                # no df_tech baseline -> just plot df_right items vs integer index
                x_idx = np.arange(len(df_right))
                dates = [d.strftime("%m/%d") for d in df_right["Date"]]
                if "foreign_hold" in df_right.columns:
                    ax_right_fore.plot(x_idx, df_right["foreign_hold"].values, linewidth=2.0, label="外資持股")
                if "foreign_net" in df_right.columns:
                    bars = df_right["foreign_net"].values
                    ax_fore2 = ax_right_fore.twinx()
                    ax_fore2.bar(x_idx, bars, alpha=0.6)
                # trust/dealer similar...
                # (simpler case kept minimal; primary path is alignment with df_tech)
                stepR = max(1, len(x_idx)//10)
                xticksR = x_idx[::stepR]
                xlabelsR = dates[::stepR]
                for a in [ax_right_k, ax_right_vol, ax_right_fore, ax_right_trust, ax_right_dealer]:
                    a.set_xticks(xticksR)
                ax_right_dealer.set_xticklabels(xlabelsR, rotation=45, ha='right')
        else:
            ax_right_fore.text(0.5, 0.5, "No Fubon institutional data", ha='center', va='center', transform=ax_right_fore.transAxes)
            ax_right_trust.set_visible(False)
            ax_right_dealer.set_visible(False)

        # Final layout: ensure no vertical gaps; hide repeated spines
        plt.subplots_adjust(left=0.06, right=0.98, top=0.94, bottom=0.08, hspace=0.0, wspace=0.18)
        # hide redundant spines between stacked axes to make them appear merged
        axes = [ax_left_k, ax_left_vol, ax_left_kd, ax_left_rsi, ax_left_macd,
                ax_right_k, ax_right_vol, ax_right_fore, ax_right_trust, ax_right_dealer]
        for i in range(len(axes)-1):
            try:
                axes[i].spines['bottom'].set_visible(False)
                axes[i+1].spines['top'].set_visible(False)
                plt.setp(axes[i].get_xticklabels(), visible=False)
            except Exception:
                pass
        # show xlabels only on bottom-most axes
        try:
            ax_left_macd.set_xticklabels(ax_left_macd.get_xticklabels(), rotation=45, ha='right')
        except Exception:
            pass

        os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)
        plt.savefig(out_png, dpi=150, bbox_inches='tight')
        plt.close(fig)
        print(f"✅ {sid} 合併圖完成 → {out_png}")
    except Exception as e:
        try:
            if fig is not None:
                plt.close(fig)
        except Exception:
            pass
        print(f"❌ plot_combined_chart({sid}) 發生錯誤：{e}")
        return

# -------------------------
# main process (保持你原本流程)
# -------------------------
def main():
    start_time = time.perf_counter()
    today_str = datetime.now().strftime("%Y%m%d")
    folder_path = os.path.join("data", today_str)
    os.makedirs(folder_path, exist_ok=True)
    print(f"📁 資料將儲存在：{folder_path}")

    # stock list
    file_list = os.path.join(folder_path, "stocknumber_nonETF_all.csv")
    if not os.path.exists(file_list):
        raise FileNotFoundError(f"❌ 找不到股票清單：{file_list}  （請把 stocknumber_nonETF_all.csv 放到 {folder_path}）")

    df_list = pd.read_csv(file_list)
    stock_ids = df_list["stock_id"].astype(str).tolist()
    print(f"共 {len(stock_ids)} 檔股票。")

    # Yahoo download (6mo)
    print("\n🚀 開始批次下載所有股票資料（約需數十秒到數分鐘，視數量）...")
    data_all = yf.download(
        tickers=stock_ids,
        period="6mo",
        interval="1d",
        group_by="ticker",
        auto_adjust=False,
        threads=True,
        progress=True,
    )

    frames = []
    for symbol in stock_ids:
        try:
            top_cols = data_all.columns.get_level_values(0)
        except Exception:
            top_cols = []
        if symbol not in top_cols:
            if symbol in data_all.columns:
                # fallback (rare)
                continue
            continue
        df_tmp = data_all[symbol].copy()
        df_tmp = df_tmp.dropna(subset=["Open", "High", "Low", "Close", "Volume"])
        df_tmp.reset_index(inplace=True)
        cleaned_symbol = symbol.replace(".TWO", "").replace(".TW", "")
        df_tmp["stock_id"] = cleaned_symbol
        df_tmp.rename(columns={"Volume": "Capacity", "Date": "Date"}, inplace=True)
        frames.append(df_tmp)

    if not frames:
        raise ValueError("❌ 沒有可用的股票資料！請先確認 yfinance 下載結果或 stock list 的格式。")

    df_all = pd.concat(frames, ignore_index=True)
    df_all = df_all.astype({"Open": float, "Close": float, "High": float, "Low": float, "Capacity": int})
    df_all.sort_values(["stock_id", "Date"], inplace=True)

    # technical columns
    print("📈 計算移動平均與量能指標...")
    df_all["MA5"] = df_all.groupby("stock_id")["Close"].transform(lambda x: x.rolling(5).mean())
    df_all["MA10"] = df_all.groupby("stock_id")["Close"].transform(lambda x: x.rolling(10).mean())
    df_all["MA20"] = df_all.groupby("stock_id")["Close"].transform(lambda x: x.rolling(20).mean())
    df_all["MA60"] = df_all.groupby("stock_id")["Close"].transform(lambda x: x.rolling(60).mean())
    df_all["VOL5"] = df_all.groupby("stock_id")["Capacity"].transform(lambda x: x.rolling(5).mean())
    df_all["VOL20"] = df_all.groupby("stock_id")["Capacity"].transform(lambda x: x.rolling(20).mean())

    # strategy functions (kept)
    def check_blackinverse(df):
        if len(df) < 2:
            return False
        D1, D = df.iloc[-2], df.iloc[-1]
        cond1 = (D1["Close"] < D1["Open"]) and (D["Close"] > D["Open"])
        cond2 = ((D1["Open"] - D1["Close"]) / D1["Open"]) >= 0.1
        cond3 = D["Close"] >= D1["Open"]
        return cond1, cond2, cond3

    def check_iamfly(df):
        if len(df) < 10:
            return False
        d2, d1, d0 = df.iloc[-3], df.iloc[-2], df.iloc[-1]
        range_d2 = (d2["Close"] - d2["Open"])
        if range_d2 <= 0:
            return False
        cond1 = (d2["Close"] > d2["Open"]) and (range_d2 /(d2["High"] - d2["Low"])  >= 0.02)
        cond2 = (d1["Close"] < d1["Open"]) and (d2["High"] < d1["High"]) and (d2["Low"] < d1["Low"])
        cond3 = (d0["Close"] >= d0["MA5"] * 0.975) or (d0["Close"] >= d0["MA10"] * 0.975)
        cond4 = (
            (d0["Capacity"] > 2000000)
            and (d0["VOL5"] > 2000000)
            and (d0["Capacity"] < d0["VOL5"])
            and (d0["Capacity"] < d2["Capacity"])
        )
        return cond1 and cond2 and cond3 and cond4

    def check_highfly_watch(df):
        if len(df) < 10:
            return False
        d1, d0 = df.iloc[-2], df.iloc[-1]
        range_d1 = (d1["Close"] - d1["Open"])
        if range_d1 <= 0:
            return False
        cond1 = range_d1 / (d1["High"] - d1["Low"]) >= 0.02
        cond2 = (d0["Close"] < d0["Open"]) and (d1["High"] < d0["High"]) and (d1["Low"] < d0["Low"])
        cond3 = (d0["Close"] > d0["MA5"] * 0.975) or (d0["Close"] > d0["MA10"] * 0.975)
        cond4 = (d0["Capacity"] > 2000000) and (d0["VOL5"] > 2000000) and (d0["Capacity"] < d1["Capacity"])
        return cond1 and cond2 and cond3 and cond4

    print("\n⚡ 開始策略篩選...")
    qualified_blackinverse = []
    qualified_iamfly = []
    qualified_highfly_watch = []

    qualified_dir = os.path.join(folder_path, "qualified_df")
    os.makedirs(qualified_dir, exist_ok=True)

    for stock_id, df in df_all.groupby("stock_id"):
        try:
            if all(check_blackinverse(df)):
                qualified_blackinverse.append(stock_id)
                df.to_csv(os.path.join(qualified_dir, f"{stock_id}_blackinverse.csv"), index=False)
            if check_iamfly(df):
                qualified_iamfly.append(stock_id)
                df.to_csv(os.path.join(qualified_dir, f"{stock_id}_iamfly.csv"), index=False)
            if check_highfly_watch(df):
                qualified_highfly_watch.append(stock_id)
                df.to_csv(os.path.join(qualified_dir, f"{stock_id}_pre_fly.csv"), index=False)
        except Exception as e:
            print(f"{stock_id} 發生錯誤：{e}")

    # export strategy lists
    pd.DataFrame(qualified_blackinverse, columns=["stock_id"]).to_csv(os.path.join(folder_path, f"{today_str}_Blackinverse.csv"), index=False)
    pd.DataFrame(qualified_iamfly, columns=["stock_id"]).to_csv(os.path.join(folder_path, f"{today_str}_iamfly.csv"), index=False)
    pd.DataFrame(qualified_highfly_watch, columns=["stock_id"]).to_csv(os.path.join(folder_path, f"{today_str}_Pre_fly.csv"), index=False)

    print("\n✅ 策略篩選完成！")
    print(f"黑反轉：{len(qualified_blackinverse)} 檔")
    print(f"黑飛舞：{len(qualified_iamfly)} 檔")
    print(f"高飛舞前期觀察：{len(qualified_highfly_watch)} 檔")

    # -------------------------
    # 擷取 Fubon 三大法人並輸出 CSV + 合併圖
    # -------------------------
    print("\n📊 以 Fubon 擷取三大法人『估計持股／買賣超』近 60 日資料...")
    end_date_str = datetime.now().strftime("%Y-%m-%d")
    start_date_str = (datetime.now() - timedelta(days=120)).strftime("%Y-%m-%d")

    records_all = []
    plot_dir = os.path.join(folder_path, "plot")
    debug_dir = os.path.join(folder_path, "fubon_debug")
    os.makedirs(plot_dir, exist_ok=True)
    os.makedirs(debug_dir, exist_ok=True)

    ok_count, fail_count = 0, 0

    strategy_groups = {
        "Blackinverse": qualified_blackinverse,
        "iamfly": qualified_iamfly,
        "Pre_fly": qualified_highfly_watch,
    }

    for strategy_name, stock_list in strategy_groups.items():
        for sid in stock_list:
            try:
                df_iv = fetch_fubon_institutional(
                    sid, start_date_str, end_date_str,
                    market_hint="auto", timeout=20, debug_dir=debug_dir
                )
                if df_iv is None or df_iv.empty:
                    print(f"{sid}：Fubon 無資料或解析失敗（已輸出 debug 檔）")
                    fail_count += 1
                    continue
                df60 = df_iv.tail(60).copy()

                # tech csv candidates
                plot_tech_candidates = [
                    os.path.join(qualified_dir, f"{sid}_iamfly.csv"),
                    os.path.join(qualified_dir, f"{sid}_pre_fly.csv"),
                    os.path.join(qualified_dir, f"{sid}_blackinverse.csv"),
                ]
                plot_tech_file = next((p for p in plot_tech_candidates if os.path.exists(p)), None)

                out_png = os.path.join(plot_dir, f"{today_str}_{strategy_name}_{sid}_combined.png")
                plot_combined_chart(df_iv, plot_tech_file, sid, strategy_name, out_png, days=60, today_str_override=today_str)

                # record flatten
                rec = {"stock_id": sid, "strategy": strategy_name}
                for i, row in enumerate(df60.itertuples(index=False), 1):
                    rec[f"date_{i}"] = row.date
                    rec[f"Foreign_hold_{i}"] = row.foreign_hold
                    rec[f"Foreign_net_{i}"] = row.foreign_net
                    rec[f"Investment_Trust_hold_{i}"] = row.trust_hold
                    rec[f"Investment_Trust_net_{i}"] = row.trust_net
                    rec[f"Dealer_hold_{i}"] = row.dealer_hold
                    rec[f"Dealer_net_{i}"] = row.dealer_net
                records_all.append(rec)

                ok_count += 1
                time.sleep(0.8 + np.random.rand() * 0.6)
            except Exception as e:
                print(f"{sid} ({strategy_name}) 抓取／繪圖失敗：{e}")
                fail_count += 1

    df_fubon = pd.DataFrame(records_all)
    csv_path_fubon = os.path.join(folder_path, f"{today_str}_fubon_holdings_net_60d.csv")
    df_fubon.to_csv(csv_path_fubon, index=False, encoding="utf-8-sig")
    print(f"✅ 已輸出 Fubon 法人資料：{csv_path_fubon}")
    print(f"✅ 三面板 PNG 輸出目錄：{plot_dir}")
    print(f"✅ 成功 {ok_count} 檔；失敗 {fail_count} 檔")
    print(f"✅ debug 目錄：{debug_dir}")

    # -------------------------
    # 技術圖批次（來源 qualified_df）
    # -------------------------
    print("\n📊 開始產生技術指標 K 線圖（從 qualified_df）...")
    tech_output_dir = os.path.join(folder_path, "plot")
    os.makedirs(tech_output_dir, exist_ok=True)

    files = [os.path.join(qualified_dir, f) for f in os.listdir(qualified_dir)
             if f.endswith(".csv") and ("_iamfly" in f or "_pre_fly" in f or "_blackinverse" in f)]

    print(f"📊 共找到 {len(files)} 個檔案，開始批次繪圖...\n")
    for f in files:
        try:
            # preserve old behavior: generate technical PNG for each qualified file
            plot_technical_chart(f, output_dir=tech_output_dir, today_str_override=today_str, save_plot=True, days=60)
        except Exception as e:
            print(f"❌ data file {f} 發生錯誤：{e}")

    print(f"\n🎯 所有技術圖表已輸出至：{tech_output_dir}")
    end_time = time.perf_counter()
    print(f"\n✅ 全部流程完成！總耗時 {end_time - start_time:.2f} 秒")

if __name__ == "__main__":
    main()
