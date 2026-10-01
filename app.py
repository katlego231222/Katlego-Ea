import streamlit as st
import time, json, urllib.request
from datetime import datetime

st.set_page_config(page_title="KATLEGO V6.1 - 4 LINES CHART", layout="centered")

st.markdown("""
<style>
.big{font-size:78px;font-weight:900;text-align:center;line-height:1}
.buy{border:4px solid #22c55e;box-shadow:0 0 35px #22c55e99;border-radius:26px;padding:16px;text-align:center;background:#0f172a}
.sell{border:4px solid #ef4444;box-shadow:0 0 35px #ef444499;border-radius:26px;padding:16px;text-align:center;background:#0f172a}
.wait{border:2px solid #334155;border-radius:26px;padding:16px;text-align:center;background:#0f172a}
.badge{background:#facc15;color:#000;padding:5px 14px;border-radius:20px;font-weight:900;font-size:12px}
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align:center'>KATLEGO <span style='color:#22c55e'>V6.1</span> 4 LINES CHART</h2>", unsafe_allow_html=True)

if 'trade' not in st.session_state: st.session_state.trade=None
if 'history' not in st.session_state: st.session_state.history=[]

def get_gold():
    try:
        with urllib.request.urlopen("https://api.gold-api.com/price/XAU", timeout=5) as r:
            return float(json.loads(r.read().decode())['price'])
    except:
        return 4159.80

price = get_gold()
st.session_state.history.append(price)
if len(st.session_state.history) > 60:
    st.session_state.history = st.session_state.history[-60:]

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

# SIGNAL LOCK
if st.session_state.trade:
    t=st.session_state.trade
    pnl = price-t['e'] if t['d']=="BUY" else t['e']-price
    is_buy = t['d']=="BUY"
    col="#22c55e" if is_buy else "#ef4444"
    box="buy" if is_buy else "sell"
    st.markdown(f"<div class='{box}'><div class='big' style='color:{col}'>{t['d']}</div><div class='badge'>🔒 LOCKED TILL TP</div><div>Entry {t['e']:.2f} | SL {t['sl']:.2f} | TP {t['tp']:.2f}<br>LIVE {price:.2f} PnL {pnl:+.2f}$</div></div>", unsafe_allow_html=True)
    if (price>=t['tp'] if is_buy else price<=t['tp']):
        st.success(f"✅ TP HIT +$12 {t['e']:.2f}->{price:.2f}"); st.session_state.trade=None; st.balloons(); time.sleep(1); st.rerun()
    if (price<=t['sl'] if is_buy else price>=t['sl']):
        st.error(f"❌ SL HIT -$3 {t['e']:.2f}->{price:.2f}"); st.session_state.trade=None; time.sleep(1); st.rerun()
else:
    if len(st.session_state.history) < 15:
        st.markdown(f"<div class='wait'><div class='big'>WAIT</div>Loading {len(st.session_state.history)}/15<br>GOLD LIVE {price:.2f}</div></div>", unsafe_allow_html=True)
    else:
        h=st.session_state.history
        e10=ema(h,10); e20=ema(h,20); r=rsi(h,14)
        low=min(h[-12:]); high=max(h[-12:])
        sig="WAIT"
        if abs(e10-e20)<1.0 and r>=25 and r<=58 and (price-low)<2.2: sig="BUY"
        elif abs(e10-e20)<1.0 and r>=42 and r<=75 and (high-price)<2.2: sig="SELL"
        if sig!="WAIT":
            e=price; sl=e-3 if sig=="BUY" else e+3; tp=e+12 if sig=="BUY" else e-12
            st.session_state.trade={'d':sig,'e':e,'sl':sl,'tp':tp}; st.rerun()
        else:
            st.markdown(f"<div class='wait'><div class='big'>WAIT</div>RSI {r:.0f} EMA {e10:.1f}/{e20:.1f} | Gold {price:.2f}</div></div>", unsafe_allow_html=True)

# ALWAYS VALUES
if st.session_state.trade:
    ev=st.session_state.trade['e']; sv=st.session_state.trade['sl']; tv=st.session_state.trade['tp']; dv=st.session_state.trade['d']
else:
    ev=price; sv=price-3; tv=price+12; dv="WAIT"

c1,c2,c3=st.columns(3)
c1.metric("ENTRY", f"{ev:.2f}", dv)
c2.metric("SHORT SL", f"{sv:.2f}", "-$3")
c3.metric("LONG TP", f"{tv:.2f}", "+$12")

# === CHART WITH 4 LINES NAMED Entry SL and TP ===
st.markdown("### 📈 Gold LIVE Chart - 4 Lines: Gold, Entry, SL, TP")

chart_data = []
# Add 60 points with 4 named lines
for p in st.session_state.history:
    chart_data.append({
        "Gold LIVE": p,
        "Entry": ev,
        "SL": sv,
        "TP": tv
    })

# This shows 4 lines with names in legend
st.line_chart(chart_data, height=400)

st.markdown(f"""
**CHART LEGEND:**
- 🔵 **Gold LIVE** = {price:.2f}
- ⚪ **Entry** = {ev:.2f}
- 🔴 **SL** = {sv:.2f} (-$3)
- 🟢 **TP** = {tv:.2f} (+$12)
""")

st.caption("If chart looks flat, wait 3 mins - need 15+ points. LOCK till TP hit - real gold-api.com")

time.sleep(10)
st.rerun()