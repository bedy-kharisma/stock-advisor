import streamlit as st
import pandas as pd
import yfinance as yf

# =========================
# STREAMLIT UI
# =========================

st.title("📊 Portfolio Capital Allocation")

capital = st.number_input(
    "Enter Capital (Rp)",
    min_value=100000,
    value=10000000,
    step=100000
)

st.write("## Capital Allocation (Lot Based + Liquidity Filter)")

# =========================
# PREPARE PORTFOLIO
# =========================

portfolio = list(zip(stocks, w_opt))
portfolio_sorted = sorted(portfolio, key=lambda x: x[1], reverse=True)

lot_size = 100
allocation_result = []

# =========================
# PROCESS STOCKS
# =========================

progress = st.progress(0)

for idx, (s, w) in enumerate(portfolio_sorted):

    progress.progress((idx + 1) / len(portfolio_sorted))

    # skip tiny weights
    if w < 0.005:
        continue

    ticker = yf.Ticker(f"{s}.JK")

    try:
        hist = ticker.history(period="5d")

        if hist.empty:
            continue

        price = hist["Close"].iloc[-1]
        volume = hist["Volume"].iloc[-1]

    except:
        continue

    # =========================
    # LIQUIDITY FILTER
    # =========================

    transaction_value = price * volume
    max_allowed = 0.10 * transaction_value

    allocated_money = capital * w

    # skip illiquid allocation
    if allocated_money > max_allowed:
        continue

    # minimum 1 lot
    min_required = price * lot_size

    if allocated_money < min_required:
        continue

    # =========================
    # LOT CALCULATION
    # =========================

    lots = int(allocated_money // min_required)
    shares = lots * lot_size

    used_money = shares * price
    leftover = allocated_money - used_money

    allocation_result.append({
        "Stock": s,
        "Weight %": round(w * 100, 2),
        "Price": round(price, 0),
        "Volume": round(volume, 0),
        "Max 10% Liquidity": round(max_allowed, 0),
        "Lots": lots,
        "Shares": shares,
        "Used Capital": round(used_money, 0),
        "Leftover": round(leftover, 0)
    })

# =========================
# SHOW RESULT
# =========================

if allocation_result:

    result_df = pd.DataFrame(allocation_result)

    st.dataframe(
        result_df,
        use_container_width=True
    )

    # =========================
    # SUMMARY
    # =========================

    total_used = result_df["Used Capital"].sum()
    total_left = capital - total_used

    st.write("## Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Capital",
        f"Rp {capital:,.0f}"
    )

    col2.metric(
        "Used Capital",
        f"Rp {total_used:,.0f}"
    )

    col3.metric(
        "Remaining",
        f"Rp {total_left:,.0f}"
    )

else:
    st.warning("No stocks passed the allocation filters.")
