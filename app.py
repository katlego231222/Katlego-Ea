import streamlit as st
import time, json, urllib.request

st.set_page_config(page_title="KATLEGO V6.2 - 5 LINES", layout="centered")

st.markdown("""
<style>
.big{font-size:72px;font-weight:900;text-align:center;line-height:1}
.buy{border:4px solid #22c55e;box-shadow:0 0 35px #22c55e99;border-radius:26px;padding:14px;text-align:center;background:#0f172a}
.sell{border:4px solid #ef4444;box-shadow:0 0 35px #ef444499;border-radius:26px;padding:14px;text-align:center;background:#0f172a}
.wait{border:2px solid #334155;border-radius:26px;padding:14px;text-align:center;background:#0f172a}
.badge{background:#facc15;color:#000;padding:5px 14px;border-radius:20px;font-weight:900;font-size:12px}
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align:center'>KATLEGO <span style='color:#22c55e'>V6.2</span> 5 LINES CHART 🔒</h2>", unsafe_allow_html=True)

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

def ema(d,p):
    if len(d)<p: return d[-1]
    k=2/(p+1); e=sum(d[:p])/p
    for x in d[p:]: e=x*k+e*(1-k)
    return e
def rsi(d,p=14):
    if len(d)<p+1: return 50
    g=l=0
    for i in range(-p,0):
        v=d[i]-d[i-1]
        if v>0: g+=v
        else: l+=-v
    if l==0: return 70
    return 100-(100/(1+g/l))

if st.session_state.trade:
    t=st.session_state.trade
    pnl=price-t['e'] if t['d']=="BUY" else t['e']-price
    is_buy=t['d']=="BUY"
    st.markdown(f"<div class='{'buy' if is_buy else 'sell'}'><div class='big' style='color:{'#22c55e' if is_buy else '#ef4444'}'>{t['d']}</div><div class='badge'>🔒 LOCKED TILL TP2</div><div>Entry {t['e']:.2f} | SL {t['sl']:.2f} | TP1 {t['tp1']:.2f} | TP2 {t['tp2']:.2f}<br>LIVE {price:.2f} PnL {pnl:+.2f}$</div></div>", unsafe_allow_html=True)
    tp2_hit=price>=t['tp2'] if is_buy else price<=t['tp2']
    sl_hit=price<=t['sl'] if is_buy else price>=t['sl']
    if tp2_hit:
        st.success(f"✅ TP2 HIT +$14 {t['e']:.2f}->{price:.2f}"); st.session_state.trade=None; st.balloons(); time.sleep(1); st.rerun()
    if sl_hit:
        st.error(f"❌ SL HIT -$3"); st.session_state.trade=None; time.sleep(1); st.rerun()
else:
    if len(st.session_state.history)<15:
        st.markdown(f"<div class='wait'><div class='big'>WAIT</div>Loading {len(st.session_state.history)}/15<br>GOLD {price:.2f}</div></div>", unsafe_allow_html=True)
    else:
        h=st.session_state.history
        e10=ema(h,10); e20=ema(h,20); r=rsi(h,14)
        low=min(h[-12:]); high=max(h[-12:])
        sig="WAIT"
        if abs(e10-e20)<1.0 and r>=25 and r<=58 and (price-low)<2.2: sig="BUY"
        elif abs(e10-e20)<1.0 and r>=42 and r<=75 and (high-price)<2.2: sig="SELL"
        if sig!="WAIT":
            e=price; sl=e-3 if sig=="BUY" else e+3; tp1=e+7 if sig=="BUY" else e-7; tp2=e+14 if sig=="BUY" else e-14
            st.session_state.trade={'d':sig,'e':e,'sl':sl,'tp1':tp1,'tp2':tp2}; st.rerun()
        else:
            st.markdown(f"<div class='wait'><div class='big'>WAIT</div>RSI {r:.0f} EMA {e10:.1f}/{e20:.1f}<br>GOLD LIVE {price:.2f}</div></div>", unsafe_allow_html=True)

if st.session_state.trade:
    ev=st.session_state.trade['e']; sv=st.session_state.trade['sl']; tp1v=st.session_state.trade['tp1']; tp2v=st.session_state.trade['tp2']; dv=st.session_state.trade['d']
else:
    ev=price; sv=price-3; tp1v=price+7; tp2v=price+14; dv="WAIT"

c1,c2,c3,c4=st.columns(4)
c1.metric("ENTRY", f"{ev:.2f}", dv)
c2.metric("SL", f"{sv:.2f}", "-$3")
c3.metric("TP1", f"{tp1v:.2f}", "+$7")
c4.metric("TP2", f"{tp2v:.2f}", "+$14")

st.markdown("### 📈 Chart - 5 Lines: Gold, Entry, SL, TP1, TP2")
chart=[]
for p in st.session_state.history:
    chart.append({"Gold LIVE":p,"Entry":ev,"SL":sv,"TP1":tp1v,"TP2":tp2v})
st.line_chart(chart, height=420)
st.caption(f"Gold {price:.2f} | Entry {ev:.2f} | SL {sv:.2f} | TP1 {tp1v:.2f} | TP2 {tp2v:.2f} | Wait 2 mins for wave")
time.sleep(10)
st.rerun()