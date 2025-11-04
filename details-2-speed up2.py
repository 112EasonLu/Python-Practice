# details-2-final-fixed.py
# 完整可執行版：多進程 + RSI safe + Optimize + 年/月圖 + 自動尋找 stock list
# Save as details-2-final-fixed.py and run: python details-2-final-fixed.py

import os
import math
import glob
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib import rcParams, font_manager
import seaborn as sns
from multiprocessing import Pool, cpu_count, freeze_support
from tqdm import tqdm

# ---------------------
# Config
# ---------------------
PRINCIPAL = 10000
FEE_RATE = 0.001425 * 0.2
TAX_RATE = 0.003
STOCK_LIST_FILENAME = "stocknumber_nonETF_all.csv"  # preferred name
# You may set this to a concrete path if you want:
# STOCK_LIST_PATH = r"d:\Personal File\Python\data\20251104\stocknumber_nonETF_all.csv"
STOCK_LIST_PATH = None  # None => script will auto-search

# ---------------------
# Helpers: find stock list
# ---------------------
def find_stock_list():
    # 1) explicit path
    if STOCK_LIST_PATH:
        if os.path.exists(STOCK_LIST_PATH):
            return STOCK_LIST_PATH
        else:
            return None

    # 2) current dir
    cur = os.path.abspath(os.getcwd())
    path1 = os.path.join(cur, STOCK_LIST_FILENAME)
    if os.path.exists(path1):
        return path1

    # 3) search data/<date>/stocknumber_nonETF_all.csv, choose latest date folder
    data_dirs = sorted(glob.glob(os.path.join(cur, "data", "*")), reverse=True)
    for d in data_dirs:
        p = os.path.join(d, STOCK_LIST_FILENAME)
        if os.path.exists(p):
            return p

    # 4) search anywhere under current dir
    found = glob.glob(os.path.join(cur, "**", STOCK_LIST_FILENAME), recursive=True)
    if found:
        return found[0]

    return None

def write_template_stock_list(outpath="stocknumber_nonETF_all_template.csv"):
    df = pd.DataFrame({
        "stock_id": ["2330.TW", "2317.TW", "2412.TW"],
        "note": ["TSMC example", "Hon Hai example", "Company example"]
    })
    df.to_csv(outpath, index=False, encoding="utf-8-sig")
    return outpath

# ---------------------
# plotting font
# ---------------------
def set_cjk_font(preferred=None):
    candidates = preferred or ["Microsoft JhengHei", "PingFang TC", "Noto Sans CJK TC", "Taipei Sans TC Beta"]
    installed = [f.name for f in font_manager.fontManager.ttflist]
    chosen = None
    for c in candidates:
        if c in installed:
            chosen = c
            break
        # fallback: partial match
        for name in installed:
            if c in name:
                chosen = name
                break
        if chosen:
            break
    if chosen:
        rcParams["font.family"] = "sans-serif"
        rcParams["font.sans-serif"] = [chosen]
        print(f"✅ Matplotlib font set: {chosen}")
    rcParams["axes.unicode_minus"] = False

set_cjk_font()

# ---------------------
# RSI safe divide & logging
# ---------------------
def safe_divide_rsi(d0, sid, df_context=None):
    try:
        if pd.isna(d0.get("RSI5")) or pd.isna(d0.get("RSI10")) or d0.get("RSI10") == 0:
            raise ValueError("RSI10 is NaN or zero")
        return (d0["RSI5"] / d0["RSI10"]) > 0.9
    except Exception as e:
        with open("debug_rsi_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] stock={sid}, date={d0.get('Date')}, error={e}\n")
            if df_context is not None:
                try:
                    f.write(df_context.tail(6).to_csv(index=False))
                except Exception:
                    f.write("failed to dump df_context\n")
            f.write("-"*80 + "\n")
        return False

# ---------------------
# Add indicators
# ---------------------
def add_indicators(df_all):
    def compute(g):
        g = g.sort_values("Date").reset_index(drop=True).copy()
        # basic smoothing
        g["MA5"] = g["Close"].rolling(5, min_periods=1).mean()
        g["MA10"] = g["Close"].rolling(10, min_periods=1).mean()
        g["VOL5"] = g["Volume"].rolling(5, min_periods=1).mean()

        # MACD
        ema12 = g["Close"].ewm(span=12, adjust=False).mean()
        ema26 = g["Close"].ewm(span=26, adjust=False).mean()
        g["DIF12_26"] = ema12 - ema26
        g["MACD9"] = g["DIF12_26"].ewm(span=9, adjust=False).mean()
        g["Hist"] = g["DIF12_26"] - g["MACD9"]

        # KD (9)
        low_min = g["Low"].rolling(9, min_periods=1).min()
        high_max = g["High"].rolling(9, min_periods=1).max()
        den = (high_max - low_min).replace(0, np.nan)
        g["RSV9"] = (g["Close"] - low_min) / den * 100
        g["9K"] = g["RSV9"].ewm(alpha=1/3, adjust=False).mean()
        g["9D"] = g["9K"].ewm(alpha=1/3, adjust=False).mean()

        # RSI 5/10
        delta = g["Close"].diff()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)
        avg_gain5 = gain.rolling(5, min_periods=1).mean()
        avg_loss5 = loss.rolling(5, min_periods=1).mean().replace(0, np.nan)
        rs5 = avg_gain5 / avg_loss5
        avg_gain10 = gain.rolling(10, min_periods=1).mean()
        avg_loss10 = loss.rolling(10, min_periods=1).mean().replace(0, np.nan)
        rs10 = avg_gain10 / avg_loss10
        g["RSI5"] = 100 - 100 / (1 + rs5)
        g["RSI10"] = 100 - 100 / (1 + rs10)

        # clean
        g.replace([np.inf, -np.inf], np.nan, inplace=True)
        g.fillna(method="ffill", inplace=True)
        g.fillna(method="bfill", inplace=True)
        return g

    # groupby apply may warn; still fine
    return df_all.groupby("stock_id", group_keys=False).apply(compute).reset_index(drop=True)

# ---------------------
# Strategy checks (use safe_divide_rsi)
# ---------------------
def check_iamfly_1(window):
    if len(window) < 10: 
        return False
    sid = window["stock_id"].iloc[-1]
    d2, d1, d0 = window.iloc[-3], window.iloc[-2], window.iloc[-1]
    try:
        if (d2["Close"] - d2["Open"]) <= 0:
            return False
        cond1 = (d2["Close"] > d2["Open"])
        cond2 = (d1["Close"] < d1["Open"]) and (d2["High"] < d1["High"]) and (d2["Low"] < d1["Low"]) and (d0["High"] < d1["High"])
        cond3 = (d0["Close"] >= d0["MA5"] * 0.98)
        macd_ok = ((d0["DIF12_26"] > 0 and d0["MACD9"] > 0 and (d0["DIF12_26"] / (d0["MACD9"] if d0["MACD9"]!=0 else np.nan) > 0.9)) 
                  or (d0["DIF12_26"] > 0 > d0["MACD9"]))
        rsi_ok = safe_divide_rsi(d0, sid, window)
        kd_ok = (d0["9K"] / (d0["9D"] if d0["9D"]!=0 else np.nan) > 0.9)
        return cond1 and cond2 and cond3 and macd_ok and rsi_ok and kd_ok
    except Exception as e:
        with open("debug_other_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] check_iamfly_1 error stock={sid}, err={e}\n")
        return False

def check_iamfly_1VOL(window):
    if len(window) < 10: 
        return False
    sid = window["stock_id"].iloc[-1]
    d2, d1, d0 = window.iloc[-3], window.iloc[-2], window.iloc[-1]
    try:
        if (d2["Close"] - d2["Open"]) <= 0:
            return False
        cond2 = (d1["Close"] < d1["Open"]) and (d2["High"] < d1["High"]) and (d2["Low"] < d1["Low"]) and (d0["High"] < d1["High"])
        cond3 = (d0["Close"] >= d0["MA5"] * 0.98)
        cond4 = (d0["Volume"] > 5_000_000)
        macd_ok = ((d0["DIF12_26"] > 0 and d0["MACD9"] > 0) or (d0["DIF12_26"] > 0 > d0["MACD9"]))
        rsi_ok = safe_divide_rsi(d0, sid, window)
        kd_ok = (d0["9K"] / (d0["9D"] if d0["9D"]!=0 else np.nan) > 0.9)
        return cond2 and cond3 and cond4 and macd_ok and rsi_ok and kd_ok
    except Exception as e:
        with open("debug_other_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] check_iamfly_1VOL error stock={sid}, err={e}\n")
        return False

def check_iamfly_Modify(window):
    if len(window) < 60:
        return False
    sid = window["stock_id"].iloc[-1]
    try:
        d2, d1, d0 = window.iloc[-3], window.iloc[-2], window.iloc[-1]
        past_60_high = window.iloc[:-2]["High"].tail(60).max()
        cond5 = d1["High"] >= past_60_high * 0.95
        cond2 = (d1["Close"] < d1["Open"]) and (d2["High"] < d1["High"]) and (d2["Low"] < d1["Low"]) and (d0["High"] < d1["High"])
        cond3 = (d0["Close"] >= d0["MA5"] * 0.98)
        cond4 = (d0["Volume"] > 10_000_000)
        macd_ok = ((d0["DIF12_26"] > 0 and d0["MACD9"] > 0) or (d0["DIF12_26"] > 0 > d0["MACD9"]))
        rsi_ok = safe_divide_rsi(d0, sid, window)
        kd_ok = (d0["9K"] / (d0["9D"] if d0["9D"]!=0 else np.nan) > 0.9)
        return cond2 and cond3 and cond4 and cond5 and macd_ok and rsi_ok and kd_ok
    except Exception as e:
        with open("debug_other_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] check_iamfly_Modify error stock={sid}, err={e}\n")
        return False

# ---------------------
# Optimize exit
# ---------------------
def choose_optimized_exit(g, i):
    if i + 2 >= len(g):
        return None
    buy_close = g.iloc[i].Close
    d1 = g.iloc[i+1]
    d2 = g.iloc[i+2]
    try:
        if d1.Open < buy_close:
            return d1.Open
        d1_return = (d1.Close / buy_close - 1) * 100
        if (d1_return < 5) or (d1.Close < d1.MA5 * 0.985):
            return d1.Close
        return (d2.Open + d2.Close) / 2
    except Exception as e:
        with open("debug_other_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] optimize error stock={g.iloc[i]['stock_id']}, idx={i}, err={e}\n")
        return d1.Close if not pd.isna(d1.Close) else buy_close

# ---------------------
# Parallel helper for find_signals
# ---------------------
def process_signal(args):
    sid, g, check_func, strat_name, window_len = args
    g = g.sort_values("Date").reset_index(drop=True)
    signals = []
    # window_len variable supported (10 for S1/S2, 60 for Modify)
    for i in range(window_len-1, len(g)-2):
        window = g.iloc[i-window_len+1:i+1]
        try:
            if check_func(window):
                signals.append({"stock_id": sid, "date": g.at[i, "Date"], "strategy": strat_name})
        except Exception as e:
            with open("debug_other_log.txt", "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now()}] process_signal error sid={sid}, idx={i}, err={e}\n")
    return signals

def find_signals(df_all, check_func, strat_name="S1", window_len=10):
    tasks = [(sid, g, check_func, strat_name, window_len) for sid, g in df_all.groupby("stock_id")]
    results = []
    if not tasks:
        return pd.DataFrame(results)
    processes = max(1, cpu_count() - 1)
    with Pool(processes=processes) as pool:
        for res in tqdm(pool.imap_unordered(process_signal, tasks), total=len(tasks), desc=f"Finding {strat_name}"):
            if res:
                results.extend(res)
    return pd.DataFrame(results)

# ---------------------
# simulate money equal split
# ---------------------
def simulate_money_equal_split(df_all, signals, exit_type):
    if signals.empty:
        return pd.DataFrame()
    trades = []
    stock_map = {sid: g.sort_values("Date").reset_index(drop=True) for sid, g in df_all.groupby("stock_id")}
    for date, grp in signals.groupby("date"):
        n = len(grp)
        capital_each = math.floor(PRINCIPAL / n)
        for _, row in grp.iterrows():
            sid = row["stock_id"]
            g = stock_map.get(sid)
            if g is None: 
                continue
            idx = g[g["Date"] == date].index
            if len(idx) == 0:
                continue
            i = idx[0]
            if i + 2 >= len(g):
                continue
            buy_price = g.at[i, "Close"]
            if exit_type == "optimize":
                sell_price = choose_optimized_exit(g, i)
            else:
                # map
                d1 = g.iloc[i+1]
                d2 = g.iloc[i+2]
                sell_price = {
                    "d1_open": d1.Open, "d1_close": d1.Close, "d1_avg": (d1.Open + d1.Close)/2,
                    "d2_open": d2.Open, "d2_close": d2.Close, "d2_avg": (d2.Open + d2.Close)/2
                }[exit_type]
            effective_buy = buy_price * (1 + FEE_RATE)
            shares = int(capital_each // effective_buy)
            if shares == 0:
                continue
            buy_gross = buy_price * shares
            buy_fee = math.ceil(buy_gross * FEE_RATE)
            sell_gross = sell_price * shares
            sell_fee = math.ceil(sell_gross * FEE_RATE)
            sell_tax = round(sell_gross * TAX_RATE)
            profit = (sell_gross - sell_fee - sell_tax) - (buy_gross + buy_fee)
            trades.append({
                "signal_date": date, "stock_id": sid,
                "buy_price": round(buy_price, 2), "sell_price": round(sell_price, 2),
                "shares": shares, "profit": round(profit, 2), "capital_each": capital_each,
                "return_%": round(profit / capital_each * 100, 2)
            })
    return pd.DataFrame(trades)

# ---------------------
# monthly/yearly stats
# ---------------------
def monthly_yearly_stats(df_trades):
    if df_trades.empty:
        return None, None
    df = df_trades.copy()
    df["date"] = pd.to_datetime(df["signal_date"])
    df["year"] = df["date"].dt.year
    df["ym"] = df["date"].dt.to_period("M").astype(str)
    monthly = df.groupby("ym")["profit"].sum().reset_index()
    monthly["cum_profit"] = monthly["profit"].cumsum()
    monthly["monthly_change_rate"] = monthly["cum_profit"].diff().fillna(monthly["cum_profit"]) / PRINCIPAL * 100
    yearly = df.groupby("year")["profit"].sum().reset_index()
    yearly["yearly_return"] = yearly["profit"] / PRINCIPAL * 100
    return monthly, yearly

# ---------------------
# plotting helpers
# ---------------------
def plot_yearly_trend(yearly_df, title, out_dir, fname):
    if yearly_df is None or yearly_df.empty:
        return
    plt.figure(figsize=(10,5))
    plt.plot(yearly_df["year"], yearly_df["yearly_return"], marker="o", linewidth=2)
    avg = yearly_df["yearly_return"].mean()
    plt.axhline(0, color="gray", linestyle="--")
    plt.axhline(avg, color="red", linewidth=2, label=f"平均: {avg:.2f}%")
    plt.title(title)
    plt.xlabel("年度"); plt.ylabel("年報酬率 (%)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, fname), dpi=150)
    plt.close()

def plot_monthly_trend(monthly_df, title, out_dir, fname):
    if monthly_df is None or monthly_df.empty:
        return
    monthly_df["ym"] = pd.to_datetime(monthly_df["ym"])
    monthly_df["year"] = monthly_df["ym"].dt.year
    monthly_df["month"] = monthly_df["ym"].dt.month
    plt.figure(figsize=(12,6))
    for y, g in monthly_df.groupby("year"):
        plt.plot(g["month"], g["monthly_change_rate"], alpha=0.4, label=str(y))
    avgm = monthly_df.groupby("month")["monthly_change_rate"].mean().reset_index()
    plt.plot(avgm["month"], avgm["monthly_change_rate"], color="red", linewidth=2.8, marker="o", label="AVG")
    plt.axhline(0, color="gray", linestyle="--")
    plt.title(title); plt.xlabel("月份"); plt.ylabel("月報酬率 (%)")
    plt.legend(ncol=4, fontsize=8)
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, fname), dpi=150)
    plt.close()

def generate_heatmap_table(monthly_df, yearly_df, title, out_dir, fname):
    if monthly_df is None or yearly_df is None:
        return
    monthly_df["ym"] = pd.to_datetime(monthly_df["ym"])
    monthly_df["year"] = monthly_df["ym"].dt.year
    monthly_df["month"] = monthly_df["ym"].dt.month
    pivot = monthly_df.pivot(index="year", columns="month", values="monthly_change_rate").fillna("")
    yearly_df = yearly_df.set_index("year")
    pivot["年化"] = yearly_df["yearly_return"].round(2)
    csvp = os.path.join(out_dir, fname.replace(".png", ".csv"))
    pivot.to_csv(csvp, encoding="utf-8-sig")
    plt.figure(figsize=(12, len(pivot)*0.5 + 2))
    sns.heatmap(pivot.replace("", None).astype(float), annot=True, fmt=".2f", cmap="RdYlGn", center=0)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, fname), dpi=150)
    plt.close()

# ---------------------
# ALL exit yearly plot (with means in labels)
# ---------------------
def plot_all_exit_yearly(all_yearly_dict, strat_name, out_dir, fname):
    plt.figure(figsize=(11,6))
    avg_map = {}
    for exit_type, yearly_df in all_yearly_dict.items():
        if yearly_df is None or yearly_df.empty: 
            continue
        # ensure sorted by year
        yearly_df = yearly_df.sort_values("year")
        avg = yearly_df["yearly_return"].mean()
        avg_map[exit_type] = avg
        plt.plot(yearly_df["year"], yearly_df["yearly_return"], marker="o", linewidth=1.6, alpha=0.7,
                 label=f"{exit_type} (年均: {avg:.2f}%)")
    if not avg_map:
        return
    overall_avg = np.mean(list(avg_map.values()))
    plt.axhline(0, color="gray", linestyle="--", linewidth=1)
    plt.axhline(overall_avg, color="red", linestyle="-", linewidth=2, label=f"整體平均: {overall_avg:.2f}%")
    plt.title(f"{strat_name} 各出場方式年度報酬率比較 (2011–2025)")
    plt.xlabel("年度"); plt.ylabel("年度報酬率 (%)")
    plt.legend(ncol=2, fontsize=8, loc="upper left", frameon=True)
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, fname), dpi=150)
    plt.close()

# ---------------------
# Main
# ---------------------
def main():
    freeze_support()
    print("Start:", datetime.now().isoformat())

    # find stock list
    stock_list_path = find_stock_list()
    if not stock_list_path:
        tpl = write_template_stock_list()
        print("❌ 未找到 stock list.")
        print(f"已建立範本檔：{tpl}")
        print("請將你的 stocknumber_nonETF_all.csv 放到程式目錄或 data/<date>/ 下，再重新執行。")
        return

    print("使用股票清單:", stock_list_path)
    df_list = pd.read_csv(stock_list_path, dtype=str)
    # Expect a column stock_id. If different, try first column.
    if "stock_id" not in df_list.columns:
        df_list.columns = df_list.columns.str.strip()
        df_list.rename(columns={df_list.columns[0]: "stock_id"}, inplace=True)

    stock_ids = df_list["stock_id"].astype(str).tolist()
    if not stock_ids:
        print("❌ 股票清單為空，請檢查檔案內容。")
        return

    # output dir
    today_str = datetime.now().strftime("%Y%m%d")
    out_dir = os.path.join("data", today_str)
    os.makedirs(out_dir, exist_ok=True)

    # Download with yfinance; keep auto_adjust default
    print("Downloading tickers...", len(stock_ids))
    try:
        df_raw = yf.download(tickers=stock_ids, period="15y", interval="1d", group_by="ticker", threads=True, progress=False)
    except Exception as e:
        print("❌ yfinance download failed:", e)
        return

    # Build unified df_all
    frames = []
    for sid in stock_ids:
        # yfinance might have keys with exact sid or sid+'.TW' etc; we assume sid as provided
        try:
            if sid in df_raw.columns.get_level_values(0):
                tmp = df_raw[sid].reset_index().copy()
            else:
                # try suffix variations
                possible = [c for c in df_raw.columns.get_level_values(0) if c.startswith(sid)]
                if possible:
                    tmp = df_raw[possible[0]].reset_index().copy()
                else:
                    # ticker missing: skip
                    print(f"⚠️ ticker not in yfinance result, skip: {sid}")
                    continue
            tmp["stock_id"] = sid
            tmp.rename(columns={"Volume": "Volume"}, inplace=True)  # keep Volume column
            frames.append(tmp)
        except Exception as e:
            print(f"⚠️ error extracting {sid}: {e}")
            continue

    if not frames:
        print("❌ 沒有可用的股票資料（yfinance 未回傳任何 ticker）")
        return

    df_all = pd.concat(frames, ignore_index=True)
    df_all.sort_values(["stock_id", "Date"], inplace=True)
    df_all.reset_index(drop=True, inplace=True)

    # add indicators
    df_all = add_indicators(df_all)
    # check indicators health
    cols_to_check = ["RSI5", "RSI10", "DIF12_26", "MACD9", "9K", "9D"]
    problems = df_all[df_all[cols_to_check].isna().any(axis=1)]
    if not problems.empty:
        print("⚠️ 發現 {} 檔股票有缺值：".format(problems['stock_id'].nunique()))
        print(problems.groupby("stock_id").size().head(10))

    # find signals for S1/S2/S3
    print("尋找訊號 (S1,S2,S3)...")
    s1 = find_signals(df_all, check_iamfly_1, "S1", 10)
    s2 = find_signals(df_all, check_iamfly_1VOL, "S2", 10)
    s3 = find_signals(df_all, check_iamfly_Modify, "S3", 60)

    all_signals = {"S1": s1, "S2": s2, "S3": s3}

    exit_types = ["d1_open","d1_close","d1_avg","d2_open","d2_close","d2_avg","optimize"]

    # Run simulate for each strategy + exit_type, save outputs and compute monthly/yearly
    for strat_name, sig_df in all_signals.items():
        if sig_df is None or sig_df.empty:
            print(f"⚠️ {strat_name} no signals, skip.")
            continue
        # prepare container to store yearly dfs for ALL_exit plot
        all_yearly = {}
        for e in exit_types:
            print(f"回測 {strat_name} - {e} ...")
            df_trades = simulate_money_equal_split(df_all, sig_df, e)
            if df_trades.empty:
                print(f"  -> {e} produced no trades.")
                continue
            # save trades csv
            trades_csv = os.path.join(out_dir, f"{today_str}_{strat_name}_{e}_split_trades.csv")
            df_trades.to_csv(trades_csv, index=False, encoding="utf-8-sig")
            # monthly/yearly
            monthly_df, yearly_df = monthly_yearly_stats(df_trades)
            # save summary csvs
            if yearly_df is not None:
                yearly_csv = os.path.join(out_dir, f"{today_str}_{strat_name}_{e}_yearly.csv")
                yearly_df.to_csv(yearly_csv, index=False, encoding="utf-8-sig")
            if monthly_df is not None:
                monthly_csv = os.path.join(out_dir, f"{today_str}_{strat_name}_{e}_monthly.csv")
                monthly_df.to_csv(monthly_csv, index=False, encoding="utf-8-sig")
            # plots
            plot_yearly_trend(yearly_df, f"{strat_name}_{e} 年度趨勢", out_dir, f"{strat_name}_{e}_yearly_trend.png")
            plot_monthly_trend(monthly_df, f"{strat_name}_{e} 月度比較", out_dir, f"{strat_name}_{e}_monthly_trend.png")
            generate_heatmap_table(monthly_df, yearly_df, f"{strat_name}_{e} 年/月報酬率表", out_dir, f"{strat_name}_{e}_performance_table.png")

            # prepare for ALL_exit yearly plot (normalize yearly_df to have 'year' & 'yearly_return')
            all_yearly[e] = yearly_df

        # after exit types loop, draw ALL_exit yearly plot
        if all_yearly:
            plot_all_exit_yearly(all_yearly, strat_name, out_dir, f"{strat_name}_ALL_exit_yearly_trend.png")

    print("Done:", datetime.now().isoformat())
    print("Outputs in:", os.path.abspath(out_dir))
    # debug logs available: debug_rsi_log.txt, debug_other_log.txt

if __name__ == "__main__":
    main()
