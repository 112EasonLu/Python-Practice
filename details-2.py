# ==========================================
# backtest_with_money_sim_equal_split_v20251103.py
# 均分資金版本（S1/S2/S3 × D1/D2 × Open/Close/Avg）
# ==========================================

import os
import math
from datetime import datetime
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib import rcParams, font_manager
import seaborn as sns

# ===============================
# Matplotlib 字型設定
# ===============================
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
    if chosen:
        rcParams["font.family"] = "sans-serif"
        rcParams["font.sans-serif"] = [chosen]
        print(f"✅ 已設定 Matplotlib 字型: {chosen}")
    rcParams["axes.unicode_minus"] = False

set_cjk_font()

def check_indicator_health(df_all):
    problems = df_all[
        df_all[["RSI5", "RSI10", "DIF12_26", "MACD9", "9K", "9D"]]
        .isna().any(axis=1)
    ]
    if not problems.empty:
        print(f"⚠️ 發現 {problems['stock_id'].nunique()} 檔股票有缺值：")
        print(problems.groupby("stock_id").size().head(10))
    else:
        print("✅ 所有指標無 NaN 或 inf 值。")
# ===============================
# 指標計算 (MACD / RSI / KD)
# ===============================
def add_indicators(df_all):
    def compute(g):
        ema12 = g["Close"].ewm(span=12, adjust=False).mean()
        ema26 = g["Close"].ewm(span=26, adjust=False).mean()
        g["DIF12_26"] = ema12 - ema26
        g["MACD9"] = g["DIF12_26"].ewm(span=9, adjust=False).mean()
        g["Hist"] = g["DIF12_26"] - g["MACD9"]

        low_min = g["Low"].rolling(9, min_periods=1).min()
        high_max = g["High"].rolling(9, min_periods=1).max()
        den = (high_max - low_min).replace(0, np.nan)
        rsv = (g["Close"] - low_min) / den * 100
        g["9K"] = rsv.ewm(alpha=1/3, adjust=False).mean()
        g["9D"] = g["9K"].ewm(alpha=1/3, adjust=False).mean()

        delta = g["Close"].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain5 = gain.ewm(5, min_periods=1).mean()
        avg_loss5 = loss.ewm(5, min_periods=1).mean().replace(0, np.nan)
        rs5 = avg_gain5 / avg_loss5
        avg_gain10 = gain.ewm(10, min_periods=1).mean()
        avg_loss10 = loss.ewm(10, min_periods=1).mean().replace(0, np.nan)
        rs10 = avg_gain10 / avg_loss10
        g["RSI5"] = 100 - (100 / (1 + rs5))
        g["RSI10"] = 100 - (100 / (1 + rs10))
        g[["RSI5","RSI10"]] = g[["RSI5","RSI10"]].fillna(50)
        return g
    return df_all.groupby("stock_id", group_keys=False).apply(compute)

# ===============================
# 策略定義（S1 / S2 / S3）
# ===============================
def check_iamfly_1(df):
    if len(df) < 10:
        return False
    d2, d1, d0 = df.iloc[-3], df.iloc[-2], df.iloc[-1]
    if (d2["Close"] - d2["Open"]) <= 0:
        return False
    cond1 = (d2["Close"] > d2["Open"])
    cond2 = (d1["Close"] < d1["Open"]) and (d2["High"] < d1["High"]) and (d2["Low"] < d1["Low"]) and (d0["High"] < d1["High"])
    cond3 = (d0["Close"] >= d0["MA5"] * 0.98)
    macd_ok = ((d0["DIF12_26"] > 0 and d0["MACD9"] > 0 and d0["DIF12_26"] / d0["MACD9"] > 0.9) or (d0["DIF12_26"] > 0 > d0["MACD9"]))
    rsi_ok = (d0["RSI5"] / d0["RSI10"] > 0.9)
    kd_ok = (d0["9K"] / d0["9D"] > 0.9)
    return cond1 and cond2 and cond3 and macd_ok and rsi_ok and kd_ok

def check_iamfly_1VOL(df):
    if len(df) < 10:
        return False
    d2, d1, d0 = df.iloc[-3], df.iloc[-2], df.iloc[-1]
    if (d2["Close"] - d2["Open"]) <= 0:
        return False
    #cond1 = (d2["Close"] > d2["Open"])
    cond2 = (d1["Close"] < d1["Open"]) and (d2["High"] < d1["High"]) and (d2["Low"] < d1["Low"]) and (d0["High"] < d1["High"])
    cond3 = (d0["Close"] >= d0["MA5"] * 0.98)
    cond4 = (d0["Capacity"] > 5_000_000)
    macd_ok = ((d0["DIF12_26"] > 0 and d0["MACD9"] > 0 and d0["DIF12_26"] / d0["MACD9"] > 0.9) or (d0["DIF12_26"] > 0 > d0["MACD9"]))
    rsi_ok = (d0["RSI5"] / d0["RSI10"] > 0.9)
    kd_ok = (d0["9K"] / d0["9D"] > 0.9)
    return cond2 and cond3 and cond4 and macd_ok and rsi_ok and kd_ok

def check_iamfly_Modify(df):
    if len(df) < 60:
        return False
    d2, d1, d0 = df.iloc[-3], df.iloc[-2], df.iloc[-1]
    if (d2["Close"] - d2["Open"]) <= 0:
        return False
    past_60_high = df.iloc[:-2]["High"].tail(60).max()
    cond5 = d1["High"] >= past_60_high * 0.95
    #cond1 = (d2["Close"] > d2["Open"])
    cond2 = (d1["Close"] < d1["Open"]) and (d2["High"] < d1["High"]) and (d2["Low"] < d1["Low"]) and (d0["High"] < d1["High"])
    cond3 = (d0["Close"] >= d0["MA5"] * 0.98)
    cond4 = (d0["Capacity"] > 10_000_000)
    macd_ok = ((d0["DIF12_26"] > 0 and d0["MACD9"] > 0 and d0["DIF12_26"] / d0["MACD9"] > 0.9) or (d0["DIF12_26"] > 0 > d0["MACD9"]))
    rsi_ok = (d0["RSI5"] / d0["RSI10"] > 0.9)
    kd_ok = (d0["9K"] / d0["9D"] > 0.9)
    return cond2 and cond3 and cond4 and cond5 and macd_ok and rsi_ok and kd_ok
# ===============================
# 動態最優化出場策略 (Optimize)
# ===============================
def choose_optimized_exit(g, i):
    """根據 D1, D2 價格決定最佳出場價格"""
    if i + 2 >= len(g):
        return None  # 沒有足夠資料

    buy_close = g.iloc[i].Close
    d1 = g.iloc[i + 1]
    d2 = g.iloc[i + 2]

    # 條件 1：D1 開盤價 < 買入日收盤價 → D1 Open 出場
    if d1.Open < buy_close:
        return d1.Open

    # 條件 2：D1 收盤漲幅未達 5%，且 D1 Close < MA5 * 0.985 → D1 Close 出場
    d1_return = (d1.Close / buy_close - 1) * 100
    if (d1_return < 5) or (d1.Close < d1.MA5 * 0.985):
        return d1.Close

    # 否則留倉到 D2 平均價出場
    return (d2.Close+ d2.Open)/2
# ===============================
# 均分資金回測
# ===============================
def simulate_money_equal_split(df_all, signals, exit_type):
    if df_all.empty or signals.empty:
        return pd.DataFrame(), pd.DataFrame()

    PRINCIPAL = 10000
    FEE_RATE = 0.001425 * 0.2
    TAX_RATE = 0.003

    signals["date"] = pd.to_datetime(signals["date"])
    df_all["Date"] = pd.to_datetime(df_all["Date"])
    recs = []

    for date, group in signals.groupby("date"):
        n = len(group)
        if n == 0: continue
        capital_each = math.floor(PRINCIPAL / n)

        for _, row in group.iterrows():
            sid = row.stock_id
            g = df_all[df_all.stock_id == sid].sort_values("Date").reset_index(drop=True)
            idx = g[g["Date"] == date].index
            if len(idx) == 0: continue
            i = idx[0]
            if i + 2 >= len(g): continue

            buy_price = g.at[i, "Close"]
            if exit_type == "optimize":
                sell_price = choose_optimized_exit(g, i)
            else:
                sell_price = {
                    "d1_open": g.iloc[i+1].Open,
                    "d1_close": g.iloc[i+1].Close,
                    "d1_avg": (g.iloc[i+1].Open + g.iloc[i+1].Close)/2,
                    "d2_open": g.iloc[i+2].Open,
                    "d2_close": g.iloc[i+2].Close,
                    "d2_avg": (g.iloc[i+2].Open + g.iloc[i+2].Close)/2,
                }[exit_type]

            effective = buy_price * (1 + FEE_RATE)
            shares = int(capital_each // effective)
            if shares == 0: continue

            buy_gross = buy_price * shares
            buy_fee = math.ceil(buy_gross * FEE_RATE)
            sell_gross = sell_price * shares
            sell_fee = math.ceil(sell_gross * FEE_RATE)
            sell_tax = round(sell_gross * TAX_RATE)
            profit = (sell_gross - sell_fee - sell_tax) - (buy_gross + buy_fee)

            recs.append({
                "signal_date": date,
                "stock_id": sid,
                "buy_price": round(buy_price, 2),
                "sell_price": round(sell_price, 2),
                "shares": shares,
                "capital_each": capital_each,
                "profit": round(profit, 2),
                "return_%": round(profit / capital_each * 100, 2)
            })

    df_trades = pd.DataFrame(recs)
    if df_trades.empty:
        return df_trades, pd.DataFrame()

    summary = df_trades.groupby("signal_date")["profit"].sum().reset_index()
    summary["cum_profit"] = summary["profit"].cumsum()
    return df_trades, summary
# ===============================
# 年度報酬率趨勢圖（Yearly Trend）
# ===============================
def plot_yearly_trend(yearly_df, strat_name, out_dir):
    if yearly_df is None or yearly_df.empty:
        return

    plt.figure(figsize=(10, 5))
    plt.plot(
        yearly_df["year"], yearly_df["yearly_return"],
        marker="o", linewidth=2.2, color="royalblue", label="年度報酬率"
    )
    plt.axhline(0, color="gray", linestyle="--", linewidth=1)
    avg = yearly_df["yearly_return"].mean()
    plt.axhline(avg, color="red", linestyle="-", linewidth=2, label=f"平均: {avg:.2f}%")

    plt.title(f"{strat_name} 年度報酬率趨勢圖 (2011–2025)")
    plt.xlabel("年度")
    plt.ylabel("年度報酬率 (%)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f"{strat_name}_yearly_trend.png"), dpi=150)
    plt.close()


# ===============================
# 月度報酬率趨勢圖（Monthly Trend）
# ===============================
def plot_monthly_trend(monthly_df, strat_name, out_dir):
    if monthly_df is None or monthly_df.empty:
        return

    # 準備資料
    monthly_df["ym"] = pd.to_datetime(monthly_df["ym"])
    monthly_df["year"] = monthly_df["ym"].dt.year
    monthly_df["month"] = monthly_df["ym"].dt.month

    plt.figure(figsize=(12, 6))

    # 各年度曲線
    for year, group in monthly_df.groupby("year"):
        plt.plot(
            group["month"], group["monthly_change_rate"],
            marker="o", linewidth=1.2, alpha=0.4, label=str(year)
        )

    # 平均曲線（每月平均）
    avg_monthly = monthly_df.groupby("month")["monthly_change_rate"].mean().reset_index()
    plt.plot(
        avg_monthly["month"], avg_monthly["monthly_change_rate"],
        color="red", linewidth=2.8, marker="o", label="AVG"
    )

    plt.axhline(0, color="gray", linestyle="--", linewidth=1)
    plt.title(f"{strat_name} 各年度月度報酬率比較圖")
    plt.xlabel("月份")
    plt.ylabel("月報酬率 (%)")
    plt.legend(ncol=4, fontsize=8, loc="upper right")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f"{strat_name}_monthly_trend.png"), dpi=150)
    plt.close()

# ===============================
# 統計績效 + 年月報表
# ===============================
def monthly_yearly_stats(df_trades):
    if df_trades.empty: return None, None
    df_trades["date"] = pd.to_datetime(df_trades["signal_date"])
    df_trades["year"] = df_trades["date"].dt.year
    df_trades["ym"] = df_trades["date"].dt.to_period("M").astype(str)

    monthly = df_trades.groupby("ym")["profit"].sum().reset_index()
    monthly["cum_profit"] = monthly["profit"].cumsum()
    monthly["monthly_change_rate"] = monthly["cum_profit"].diff().fillna(monthly["cum_profit"]) / 10000 * 100

    yearly = df_trades.groupby("year")["profit"].sum().reset_index()
    yearly["yearly_return"] = yearly["profit"] / 10000 * 100
    return monthly, yearly

def generate_summary_table(monthly_df, yearly_df, strat_name, out_dir):
    if monthly_df is None or monthly_df.empty: return
    monthly_df["ym"] = pd.to_datetime(monthly_df["ym"])
    monthly_df["year"] = monthly_df["ym"].dt.year
    monthly_df["month"] = monthly_df["ym"].dt.month
    pivot = monthly_df.pivot(index="year", columns="month", values="monthly_change_rate").fillna("")
    yearly_df = yearly_df.set_index("year")
    pivot["年化"] = yearly_df["yearly_return"].round(2)
    csv_path = os.path.join(out_dir, f"{strat_name}_performance_table.csv")
    pivot.to_csv(csv_path, encoding="utf-8-sig")
    plt.figure(figsize=(12, len(pivot) * 0.5 + 2))
    sns.heatmap(pivot.replace("", None).astype(float), annot=True, fmt=".2f", cmap="RdYlGn", center=0)
    plt.title(f"{strat_name} 年度 × 月份報酬率表格 (%)")
    plt.xlabel("月份")
    plt.ylabel("年份")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f"{strat_name}_performance_table.png"), dpi=150)
    plt.close()

# ===============================
# 主程式
# ===============================
def main():
    today_str = datetime.now().strftime("%Y%m%d")
    out_dir = os.path.join("data", today_str)
    os.makedirs(out_dir, exist_ok=True)

    file_list = os.path.join(out_dir, "stocknumber_nonETF_all.csv")
    if not os.path.exists(file_list):
        print(f"❌ 找不到股票清單: {file_list}")
        return

    df_list = pd.read_csv(file_list)
    stock_ids = df_list["stock_id"].astype(str).tolist()

    df_all = yf.download(tickers=stock_ids, period="15y", interval="1d", group_by="ticker", threads=True, auto_adjust=False)
    if df_all.empty:
        print("❌ 資料下載失敗")
        return

    frames = []
    for symbol in stock_ids:
        if symbol not in df_all.columns.get_level_values(0): continue
        df_tmp = df_all[symbol].dropna().reset_index()
        df_tmp["stock_id"] = symbol.replace(".TW", "").replace(".TWO", "")
        df_tmp.rename(columns={"Volume":"Capacity"}, inplace=True)
        frames.append(df_tmp)
    df_all = pd.concat(frames, ignore_index=True)
    df_all.sort_values(["stock_id","Date"], inplace=True)
    df_all["MA5"] = df_all.groupby("stock_id")["Close"].transform(lambda x: x.rolling(5,1).mean())
    df_all["MA10"] = df_all.groupby("stock_id")["Close"].transform(lambda x: x.rolling(10,1).mean())
    df_all["VOL5"] = df_all.groupby("stock_id")["Capacity"].transform(lambda x: x.rolling(5,1).mean())
    df_all = add_indicators(df_all)
    check_indicator_health(df_all)
    s1_signals = find_signals(df_all, check_iamfly_1, "S1", 10)
    s2_signals = find_signals(df_all, check_iamfly_1VOL, "S2", 10)
    s3_signals = find_signals(df_all, check_iamfly_Modify, "S3", 60)
    all_signals = {"S1": s1_signals, "S2": s2_signals, "S3": s3_signals}
    exit_types = ["d1_open", "d1_close", "d1_avg", "d2_open", "d2_close", "d2_avg", "optimize"]

    all_yearly_data = {}  # 暫存每個策略的年度資料
    for strat_name, sig_df in all_signals.items():
        if sig_df.empty: continue
        for e in exit_types:
            df_trades, daily_summary = simulate_money_equal_split(df_all, sig_df, e)
            if df_trades.empty: continue
            df_trades.to_csv(os.path.join(out_dir, f"{today_str}_{strat_name}_{e}_split_trades.csv"), index=False, encoding="utf-8-sig")
            daily_summary.to_csv(os.path.join(out_dir, f"{today_str}_{strat_name}_{e}_split_summary.csv"), index=False, encoding="utf-8-sig")
            monthly_df, yearly_df = monthly_yearly_stats(df_trades)
            generate_summary_table(monthly_df, yearly_df, f"{strat_name}_{e}", out_dir)
            plot_yearly_trend(yearly_df, f"{strat_name}_{e}", out_dir)
            plot_monthly_trend(monthly_df, f"{strat_name}_{e}", out_dir)
            # 暫存每個 exit_type 的年度資料
            if strat_name not in all_yearly_data:
                all_yearly_data[strat_name] = {}
            all_yearly_data[strat_name][e] = yearly_df
    # ===============================
    # 繪製整合年度趨勢圖（各出場方式比較）
    # ===============================
    for strat_name, yearly_dict in all_yearly_data.items():
        plt.figure(figsize=(10, 6))

        avg_records = {}  # 暫存各出場方式平均報酬

        for exit_type, yearly_df in yearly_dict.items():
            if yearly_df is None or yearly_df.empty:
                continue

            avg_val = yearly_df["yearly_return"].mean()
            avg_records[exit_type] = avg_val

            plt.plot(
                yearly_df["year"], yearly_df["yearly_return"],
                marker="o", linewidth=1.6, alpha=0.7,
                label=f"{exit_type} (年均: {avg_val:.2f}%)"
            )

        # 輔助線
        plt.axhline(0, color="gray", linestyle="--", linewidth=1)

        # 各策略總平均
        overall_avg = np.mean(list(avg_records.values()))
        plt.axhline(overall_avg, color="red", linestyle="-", linewidth=2,
                    label=f"整體平均: {overall_avg:.2f}%")

        plt.title(f"{strat_name} 各出場方式年度報酬率比較 (2011–2025)")
        plt.xlabel("年度")
        plt.ylabel("年度報酬率 (%)")
        plt.legend(ncol=2, fontsize=8, loc="upper left", frameon=True)
        plt.grid(True, linestyle="--", alpha=0.4)
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, f"{strat_name}_ALL_exit_yearly_trend.png"), dpi=150)
        plt.close()    
    print("✅ 所有均分資金回測完成")

# ===============================
# 輔助：找訊號
# ===============================
def find_signals(df_all, check_func, strat_name="S1", window_len=10):
    signals = []
    for sid, g in df_all.groupby("stock_id"):
        g = g.sort_values("Date").reset_index(drop=True)
        for i in range(window_len-1, len(g)-2):
            window = g.iloc[i-window_len+1:i+1].reset_index(drop=True)
            if check_func(window):
                signals.append({"stock_id": sid, "idx": i, "date": g.at[i,"Date"], "strategy": strat_name})
    return pd.DataFrame(signals)

if __name__ == "__main__":
    main()
    
