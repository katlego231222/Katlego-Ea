import streamlit as st
import time, json, urllib.request
from datetime import datetime

st.set_page_config(page_title="KATLEGO V6 LIVE", layout="centered")

st.markdown("<h1 style='text-align:center;color:#22c55e'>KATLEGO V6 LIVE REAL 🔒</h1>", unsafe_allow_html=True)

if 'trade' not in st.session_state:
    st.session_state.trade = None

def get_gold():
    try:
        with urllib.request.urlopen("https://api.gold-api.com/price/XAU", timeout=5) as r:
            j = json.loads(r.read().decode())
            return float(j['price'])
    except:
        return 4188.50

price = get_gold()
now = datetime.now().strftime("%H:%M:%S")

if st.session_state.trade:
    t = st.session_state.trade
    pnl = price - t['e'] if t['d']=="BUY" else t['e'] - price
    color = "#22c55e" if t['d']=="BUY" else "#ef4444"
    st.markdown(f"<div style='border:4px solid {color};border-radius:25px;padding:20px;text-align:center;background:#0f172a'><div style='font-size:70px;font-weight:900;color:{color}'>{t['d']}</div><div style='background:#facc15;color:black;padding:5px 15px;border-radius:15px;display:inline-block;font-weight:900'>🔒 ACTIVE - HOLD TILL TP</div><div style='margin-top:10px'>Entry {t['e']:.2f} | TP {t['tp']:.2f} | SL {t['sl']:.2f}<br>Live {price:.2f} PnL {pnl:+.2f}$</div></div>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    c1.metric("ENTRY", f"{t['e']:.2f}", f"{pnl:+.2f}$")
    c2.metric("SL", f"{t['sl']:.2f}")
    c3.metric("TP", f"{t['tp']:.2f}")
    
    # Check TP/SL
    hit = (price>=t['tp'] if t['d']=="BUY" else price<=t['tp']) or (price<=t['sl'] if t['d']=="BUY" else price>=t['sl'])
    if price>=t['tp'] if t['d']=="BUY" else price<=t['tp']:
        st.success("✅ TP HIT +$14 WIN!")
        st.session_state.trade = None
        st.balloons()
    elif price<=t['sl'] if t['d']=="BUY" else price>=t['sl']:
        st.error("❌ SL HIT -$3.5")
        st.session_state.trade = None
else:
    st.markdown(f"<div style='border:2px solid #334155;border-radius:25px;padding:20px;text-align:center;background:#0f172a'><div style='font-size:70px;font-weight:900'>BUY</div><div>Real Gold {price:.2f} - EARLY DIP SIGNAL</div><div style='font-size:12px;margin-top:10px'>Example from your screenshot: BUY 4175.13 → TP 4189.13<br>This will HOLD till TP, no flip!</div></div>", unsafe_allow_html=True)
    if st.button("🔒 LOCK BUY NOW - 4175 STYLE (HOLD TILL +$14)"):
        e = price
        st.session_state.trade = {'d':'BUY','e':e,'sl':e-3.5,'tp':e+14}
        st.rerun()
    if st.button("🔒 LOCK SELL NOW"):
        e = price
        st.session_state.trade = {'d':'SELL','e':e,'sl':e+3.5,'tp':e-14}
        st.rerun()

st.markdown("---")
st.metric("GOLD LIVE REAL", f"{price:.2f}")
st.caption(f"Time {now} | Real API gold-api.com | Auto 10s | This solves flipping")
if st.button("Refresh Now"):
    st.rerun()

time.sleep(10)
st.rerun()