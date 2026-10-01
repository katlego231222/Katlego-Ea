import streamlit as st
import pandas as pd
import time
import requests
import pytz
from datetime import datetime

st.set_page_config(page_title="KATLEGO V6 LIVE", layout="centered")

st.markdown("""
<style>
.big-signal{font-size:80px;font-weight:900;text-align:center}
.buy-box{border:4px solid #22c55e;box-shadow:0 0 40px #22c55e88;border-radius:28px;padding:20px;text-align:center;background:#0f172a}
.sell-box{border:4px solid #ef4444;box-shadow:0 0 40px #ef444488;border-radius:28px;padding:20px;text-align:center;background:#0f172a}
.wait-box{border:2px solid #334155;border-radius:28px;padding:20px;text-align:center;background:#0f172a}
.lock-badge{background:#facc15;color:black;padding:8px 16px;border-radius:20px;font-weight:900;display:inline-block}
</style>
""", unsafe_allow_html=True)

st.markdown("<h3 style='text-align:center'>KATLEGO <span style='color:#22c55e'>V6 LIVE REAL</span> 🔒 HOLD TILL TP</h3>", unsafe_allow_html=True)

if 'active_trade' not in st.session_state:
    st.session_state.active_trade = None
if 'price_history' not in st.session_state:
    st.session_state.price_history = []
if 'stats' not in st.session_state:
    st.session_state.stats = {'total':0,'wins':0}

def get_live_gold():
    try:
        # Free gold API - real price
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
        return float(r['price'])
    except:
        try:
            # Backup API
            r = requests.get("https://data-asg.goldprice.org/dbXRates/USD", timeout=5).json()
            for item in r['items']:
                if item['curr'] == 'XAU':
                    return float(item['xauPrice'])
        except:
            pass
    return 4185.0  # fallback

price = get_live_gold()

# Keep history for EMA simulation
st.session_state.price_history.append(price)
if len(st.session_state.price_history) > 100:
    st.session_state.price_history = st.session_state.price_history[-100:]

close = pd.Series(st.session_state.price_history)

sa = datetime.now(pytz.timezone('Africa/Johannesburg')).strftime("%H:%M:%S")

# Simple signal logic based on recent move
if len(close) < 15:
    signal_text = "LOADING REAL PRICE..."
    r14 = 50
else:
    e10 = close.ewm(span=10, adjust=False).mean().iloc[-1]
    e20 = close.ewm(span=20, adjust=False).mean().iloc[-1]
    delta = close.diff()
    gain = delta.where(delta>0,0).rolling(14).mean().iloc[-1]
    loss = (-delta.where(delta<0,0)).rolling(14).mean().iloc[-1]
    r14 = 100 - (100/(1+gain/(loss+1e-9))) if loss!=0 else 50
    low15 = close.tail(15).min()
    high15 = close.tail(15).max()

if st.session_state.active_trade:
    at = st.session_state.active_trade
    pnl = price - at['entry'] if at['dir']=="BUY" else at['entry'] - price
    if at['dir']=="BUY":
        hit_tp = price >= at['tp']
        hit_sl = price <= at['sl']
    else:
        hit_tp = price <= at['tp']
        hit_sl = price >= at['sl']
    box = "buy-box" if at['dir']=="BUY" else "sell-box"
    st.markdown(f"<div class='{box}'><div class='big-signal'>{at['dir']}</div><div class='lock-badge'>🔒 ACTIVE HOLD TILL TP/SL - REAL GOLD</div><div style='font-size:12px;margin-top:8px'>Entry {at['entry']:.2f} → TP {at['tp']:.2f} SL {at['sl']:.2f}<br>Live {price:.2f} | PnL {pnl:+.2f}$</div></div>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    c1.metric("ENTRY", f"{at['entry']:.2f}", f"{pnl:+.2f}$")
    c2.metric("SHORT SL", f"{at['sl']:.2f}", "-$3.5")
    c3.metric("LONG TP", f"{at['tp']:.2f}", "+$14")
    st.progress(min(100, max(0, int((pnl+3.5)/17.5*100))))
    st.caption(f"Real Gold {price:.2f} To TP ${at['tp']-price if at['dir']=='BUY' else price-at['tp']:.2f} | SA {sa} | 🔒 Will NOT flip till hit")
    if hit_tp or hit_sl:
        if hit_tp:
            st.success(f"✅ TP HIT +$14 WIN at {price:.2f}")
            st.session_state.stats['wins']+=1
        else:
            st.error(f"❌ SL HIT -$3.5 at {price:.2f}")
        st.session_state.active_trade = None
        st.session_state.stats['total']+=1
        st.balloons()
        time.sleep(2)
        st.rerun()
    if st.button("✅ Mark TP HIT +$14 (when MT5 hits)"):
        st.session_state.active_trade=None
        st.session_state.stats['wins']+=1
        st.session_state.stats['total']+=1
        st.rerun()
else:
    if len(close) < 15:
        st.markdown(f"<div class='wait-box'><div class='big-signal'>WAIT</div><div>Loading real gold... {price:.2f}</div></div>", unsafe_allow_html=True)
    else:
        sig = "WAIT"
        # Early dip logic
        if e10>=e20-0.6 and e10<=e20+0.8 and r14>=36 and r14<=58 and (price-low15)<2.5:
            sig="BUY"
        elif e10>=e20-0.8 and e10<=e20+0.6 and r14>=42 and r14<=68 and (high15-price)<2.5:
            sig="SELL"
        if sig!="WAIT":
            entry=price
            sl=entry-3.5 if sig=="BUY" else entry+3.5
            tp=entry+14 if sig=="BUY" else entry-14
            st.session_state.active_trade={'dir':sig,'entry':entry,'sl':sl,'tp':tp}
            st.rerun()
        else:
            st.markdown(f"<div class='wait-box'><div class='big-signal'>WAIT</div><div style='font-size:11px'>RSI {r14:.0f} | Gold {price:.2f} | Scanning early dip...<br>BUY when flat + RSI 36-58 + near 15-bar low</div></div>", unsafe_allow_html=True)

st.markdown("---")
a,b = st.columns(2)
a.metric("GOLD LIVE REAL", f"{price:.2f}")
b.metric("Trades", f"{st.session_state.stats['total']}", f"{st.session_state.stats['wins']} wins")
st.caption(f"Real API gold-api.com | SA {sa} | Auto 10s | HOLD TILL TP - solves flipping")
time.sleep(10)
st.rerun()