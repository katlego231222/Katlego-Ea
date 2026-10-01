import streamlit as st
import yfinance as yf
import pandas as pd
import time
import pytz
from datetime import datetime

st.set_page_config(page_title="KATLEGO V6 LIVE", layout="centered")

st.markdown("""
<style>
.big-signal{font-size:85px;font-weight:900;text-align:center}
.buy-box{border:4px solid #22c55e;box-shadow:0 0 40px #22c55e88;border-radius:28px;padding:20px;text-align:center;background:#0f172a}
.sell-box{border:4px solid #ef4444;box-shadow:0 0 40px #ef444488;border-radius:28px;padding:20px;text-align:center;background:#0f172a}
.wait-box{border:2px solid #334155;border-radius:28px;padding:20px;text-align:center;background:#0f172a}
.lock-badge{background:#facc15;color:black;padding:8px 16px;border-radius:20px;font-weight:900;display:inline-block}
</style>
""", unsafe_allow_html=True)

st.markdown("<h3 style='text-align:center'>KATLEGO <span style='color:#22c55e'>V6 LIVE REAL</span> 🔒 HOLD TILL TP</h3>", unsafe_allow_html=True)

if 'active_trade' not in st.session_state:
    st.session_state.active_trade = None
if 'stats' not in st.session_state:
    st.session_state.stats = {'total':0,'wins':0}

def ema(s,p):
    return s.ewm(span=p,adjust=False).mean()

def rsi(s,p=14):
    d=s.diff()
    g=(d.where(d>0,0)).rolling(window=p).mean()
    l=(-d.where(d<0,0)).rolling(window=p).mean()
    rs=g/(l+1e-9)
    return 100-(100/(1+rs))

@st.cache_data(ttl=30)
def get_data():
    try:
        d=yf.download("GC=F",period="2d",interval="5m",progress=False)
        if d.empty:
            d=yf.download("XAUUSD=X",period="2d",interval="5m",progress=False)
        return d
    except:
        return pd.DataFrame()

data=get_data()

if data.empty:
    st.error("No data - retry in 5s")
    time.sleep(5)
    st.rerun()

close=data['Close']
if isinstance(close, pd.DataFrame):
    close=close.iloc[:,0]

price=float(close.iloc[-1])
sa=datetime.now(pytz.timezone('Africa/Johannesburg')).strftime("%H:%M:%S")

if st.session_state.active_trade:
    at=st.session_state.active_trade
    pnl=price-at['entry'] if at['dir']=="BUY" else at['entry']-price
    if at['dir']=="BUY":
        hit_tp=price>=at['tp']
        hit_sl=price<=at['sl']
    else:
        hit_tp=price<=at['tp']
        hit_sl=price>=at['sl']
    box="buy-box" if at['dir']=="BUY" else "sell-box"
    st.markdown(f"<div class='{box}'><div class='big-signal'>{at['dir']}</div><div class='lock-badge'>🔒 ACTIVE HOLD TILL TP</div><div style='font-size:12px'>Entry {at['entry']:.2f} → TP {at['tp']:.2f} SL {at['sl']:.2f}<br>Live {price:.2f} PnL {pnl:+.2f}$</div></div>",unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    c1.metric("ENTRY",f"{at['entry']:.2f}",f"{pnl:+.2f}$")
    c2.metric("SHORT SL",f"{at['sl']:.2f}")
    c3.metric("LONG TP",f"{at['tp']:.2f}")
    st.progress(min(100,max(0,int((pnl+3.5)/17.5*100))))
    st.caption(f"Real {price:.2f} SA {sa} LOCKED no flip till TP hit")
    if hit_tp or hit_sl:
        if hit_tp:
            st.success(f"✅ TP HIT +$14 at {price:.2f}")
            st.session_state.stats['wins']+=1
        else:
            st.error(f"❌ SL HIT -$3.5")
        st.session_state.active_trade=None
        st.session_state.stats['total']+=1
        st.balloons()
        time.sleep(3)
        st.rerun()
else:
    e10=ema(close,10).iloc[-1]
    e20=ema(close,20).iloc[-1]
    r14=rsi(close,14).iloc[-1]
    r7=rsi(close,7).iloc[-1]
    low15=close.tail(15).min()
    high15=close.tail(15).max()
    sig="WAIT"
    if e10>=e20-0.6 and e10<=e20+0.8 and r14>=36 and r14<=58 and r7>43 and (price-low15)<3.0:
        sig="BUY"
    elif e10>=e20-0.8 and e10<=e20+0.6 and r14>=42 and r14<=65 and r7<57 and (high15-price)<3.0:
        sig="SELL"
    if sig!="WAIT":
        entry=price
        sl=entry-3.5 if sig=="BUY" else entry+3.5
        tp=entry+14 if sig=="BUY" else entry-14
        st.session_state.active_trade={'dir':sig,'entry':entry,'sl':sl,'tp':tp}
        st.rerun()
    else:
        st.markdown(f"<div class='wait-box'><div class='big-signal'>WAIT</div><div style='font-size:11px'>RSI {r14:.0f} Gold {price:.2f} Scanning...</div></div>",unsafe_allow_html=True)

st.markdown("---")
a,b=st.columns(2)
a.metric("GOLD LIVE REAL",f"{price:.2f}")
b.metric("Stats",f"{st.session_state.stats['total']}",f"{st.session_state.stats['wins']} wins")
st.caption(f"SA {sa} | Auto 15s | HOLD TILL TP logic")
time.sleep(15)
st.rerun()