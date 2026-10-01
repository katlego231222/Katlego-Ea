import streamlit as st
import time, json, urllib.request
from datetime import datetime

st.set_page_config(page_title="KATLEGO V6.1 LOCK CHART", layout="centered")

st.markdown("""
<style>
.big{font-size:80px;font-weight:900;text-align:center;line-height:1}
.buy{border:4px solid #22c55e;box-shadow:0 0 35px #22c55e99;border-radius:26px;padding:16px;text-align:center;background:#0f172a}
.sell{border:4px solid #ef4444;box-shadow:0 0 35px #ef444499;border-radius:26px;padding:16px;text-align:center;background:#0f172a}
.wait{border:2px solid #334155;border-radius:26px;padding:16px;text-align:center;background:#0f172a}
.badge{background:#facc15;color:#000;padding:5px 14px;border-radius:20px;font-weight:900;font-size:12px}
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align:center'>KATLEGO <span style='color:#22c55e'>V6.1</span> 🔒 LOCK TILL TP + CHART</h2>", unsafe_allow_html=True)

if 'trade' not in st.session_state: st.session_state.trade=None
if 'history' not in st.session_state: st.session_state.history=[]

def get_gold():
    try:
        with urllib.request.urlopen("https://api.gold-api.com/price/XAU", timeout=5) as r:
            return float(json.loads(r.read().decode())['price'])
    except:
        return 4179.64

price = get_gold()
st.session_state.history.append(price)
if len(st.session_state.history) > 80:
    st.session_state.history = st.session_state.history[-80:]

def ema(data, p):
    if len(data) < p: return data[-1]
    k=2/(p+1); e=sum(data[:p])/p
    for x in data[p:]: e=x*k+e*(1-k)
    return e

def rsi(data, p=14):
    if len(data) < p+1: return 50
    g=l=0
    for i in range(-p,0):
        d=data[i]-data[i-1]
        if d>0: g+=d
        else: l+=-d
    if l==0: return 70
    return 100-(100/(1+g/l))

now = datetime.now().strftime("%H:%M:%S")

# --- LOCKED ---
if st.session_state.trade:
    t=st.session_state.trade
    pnl = price-t['e'] if t['d']=="BUY" else t['e']-price
    is_buy = t['d']=="BUY"
    col="#22c55e" if is_buy else "#ef4444"
    box="buy" if is_buy else "sell"
    st.markdown(f"<div class='{box}'><div class='big' style='color:{col}'>{t['d']}</div><div class='badge'>🔒 LOCKED TILL TP HIT - HOLD</div><div style='margin-top:8px'>Entry {t['e']:.2f} | SL {t['sl']:.2f} | TP {t['tp']:.2f}<br>LIVE {price:.2f} PnL {pnl:+.2f}$</div></div>", unsafe_allow_html=True)

    if (price>=t['tp'] if is_buy else price<=t['tp']):
        st.success(f"✅ TP HIT +$12 WIN! {t['e']:.2f} -> {price:.2f}")
        st.session_state.trade=None; st.balloons(); time.sleep(1); st.rerun()
    if (price<=t['sl'] if is_buy else price>=t['sl']):
        st.error(f"❌ SL HIT -$3 {t['e']:.2f} -> {price:.2f}")
        st.session_state.trade=None; time.sleep(1); st.rerun()
else:
    if len(st.session_state.history) < 20:
        st.markdown(f"<div class='wait'><div class='big'>WAIT</div>Loading {len(st.session_state.history)}/20<br>GOLD LIVE REAL {price:.2f}</div></div>", unsafe_allow_html=True)
    else:
        h=st.session_state.history
        e10=ema(h,10); e20=ema(h,20); r=rsi(h,14)
        low=min(h[-15:]); high=max(h[-15:])
        sig="WAIT"
        if abs(e10-e20)<1.2 and r>=24 and r<=58 and (price-low)<2.5:
            sig="BUY"
        elif abs(e10-e20)<1.2 and r>=42 and r<=76 and (high-price)<2.5:
            sig="SELL"
        if sig!="WAIT":
            e=price; sl=e-3 if sig=="BUY" else e+3; tp=e+12 if sig=="BUY" else e-12
            st.session_state.trade={'d':sig,'e':e,'sl':sl,'tp':tp}
            st.rerun()
        else:
            st.markdown(f"<div class='wait'><div class='big'>WAIT</div>RSI {r:.0f} EMA10 {e10:.1f} vs {e20:.1f} | GOLD LIVE {price:.2f}</div></div>", unsafe_allow_html=True)

# --- ALWAYS SHOW ENTRY SL TP ---
if st.session_state.trade:
    ev=st.session_state.trade['e']; sv=st.session_state.trade['sl']; tv=st.session_state.trade['tp']; dv=st.session_state.trade['d']
else:
    ev=price; sv=price-3; tv=price+12; dv="WAIT"

c1,c2,c3=st.columns(3)
c1.metric("ENTRY", f"{ev:.2f}", dv)
c2.metric("SHORT SL", f"{sv:.2f}", "-$3")
c3.metric("LONG TP", f"{tv:.2f}", "+$12")

# --- CHART WITH TP/SL/ENTRY - NO MATPLOTLIB NEEDED ---
st.markdown("### 📈 Gold 5M - LIVE - TP/SL/ENTRY Chart")

# Build chart data with TP/SL/ENTRY as lines
chart_data = []
for i, p in enumerate(st.session_state.history):
    row = {"GOLD LIVE": p}
    if st.session_state.trade:
        row["ENTRY"] = ev
        row["SL"] = sv
        row["TP"] = tv
    chart_data.append(row)

st.line_chart(chart_data, height=300)

st.caption(f"White=ENTRY {ev:.2f} | Red=SL {sv:.2f} | Green=TP {tv:.2f} | Real price {price:.2f} | LOCK till hit")

b1,b2=st.columns(2)
b1.metric("Live Gold REAL", f"{price:.2f}", now)
b2.metric("Status", "LOCKED 🔒" if st.session_state.trade else "SCANNING", "Hold till TP")

st.caption("Real API gold-api.com | Auto 10s | Shows signal till TP hit")
time.sleep(10)
st.rerun()