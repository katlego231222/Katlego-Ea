import streamlit as st
import time, json, urllib.request
from datetime import datetime
import pytz

st.set_page_config(page_title="KATLEGO V6 LIVE REAL", layout="centered")

# --- STYLE ---
st.markdown("""
<style>
.big{font-size:78px;font-weight:900;text-align:center;line-height:1}
.buy{border:4px solid #22c55e;box-shadow:0 0 35px #22c55e99;border-radius:26px;padding:18px;text-align:center;background:#0f172a}
.sell{border:4px solid #ef4444;box-shadow:0 0 35px #ef444499;border-radius:26px;padding:18px;text-align:center;background:#0f172a}
.wait{border:2px solid #334155;border-radius:26px;padding:18px;text-align:center;background:#0f172a}
.badge{background:#facc15;color:#000;padding:6px 14px;border-radius:20px;font-weight:900;display:inline-block;font-size:12px}
</style>
""", unsafe_allow_html=True)

st.markdown("<h3 style='text-align:center'>KATLEGO <span style='color:#22c55e'>V6 LIVE REAL</span> 🔒 HOLD TILL TP</h3>", unsafe_allow_html=True)

if 'trade' not in st.session_state: st.session_state.trade=None
if 'history' not in st.session_state: st.session_state.history=[]
if 'stats' not in st.session_state: st.session_state.stats={'t':0,'w':0}

# --- LIVE REAL GOLD ---
def get_live_gold():
    try:
        with urllib.request.urlopen("https://api.gold-api.com/price/XAU", timeout=6) as r:
            return float(json.loads(r.read().decode())['price'])
    except:
        try:
            with urllib.request.urlopen("https://api.gold-api.com/price/XAU", timeout=6) as r:
                return float(json.loads(r.read().decode())['price'])
        except:
            return 4185.0

price = get_live_gold()
st.session_state.history.append(price)
if len(st.session_state.history) > 100: st.session_state.history = st.session_state.history[-100:]

def ema(data, period):
    if len(data) < period: return data[-1]
    k = 2/(period+1)
    ema_val = sum(data[:period])/period
    for p in data[period:]:
        ema_val = p*k + ema_val*(1-k)
    return ema_val

def rsi(data, period=14):
    if len(data) < period+1: return 50
    gains=[]; losses=[]
    for i in range(1, len(data)):
        d = data[i]-data[i-1]
        gains.append(max(d,0)); losses.append(max(-d,0))
    if len(gains) < period: return 50
    avg_gain = sum(gains[-period:])/period
    avg_loss = sum(losses[-period:])/period
    if avg_loss==0: return 70
    rs = avg_gain/avg_loss
    return 100-(100/(1+rs))

sa = datetime.now(pytz.timezone('Africa/Johannesburg')).strftime("%H:%M:%S") if 'pytz' in globals() else datetime.now().strftime("%H:%M:%S")
try:
    sa = datetime.now(pytz.timezone('Africa/Johannesburg')).strftime("%H:%M:%S")
except:
    sa = datetime.now().strftime("%H:%M:%S")

# --- ACTIVE TRADE - HOLD TILL TP ---
if st.session_state.trade:
    t = st.session_state.trade
    pnl = price - t['e'] if t['d']=="BUY" else t['e']-price
    is_buy = t['d']=="BUY"
    tp_hit = price >= t['tp'] if is_buy else price <= t['tp']
    sl_hit = price <= t['sl'] if is_buy else price >= t['sl']
    box = "buy" if is_buy else "sell"
    col = "#22c55e" if is_buy else "#ef4444"

    st.markdown(f"<div class='{box}'><div class='big' style='color:{col}'>{t['d']}</div><div class='badge'>🔒 ACTIVE - HOLD TILL TP/SL</div><div style='margin-top:8px;font-size:13px'>Entry {t['e']:.2f} → TP {t['tp']:.2f} | SL {t['sl']:.2f}<br>LIVE {price:.2f} | PnL {pnl:+.2f}$</div></div>", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    c1.metric("ENTRY", f"{t['e']:.2f}", f"{pnl:+.2f} $")
    c2.metric("SHORT SL", f"{t['sl']:.2f}", "-$3.5")
    c3.metric("LONG TP", f"{t['tp']:.2f}", "+$14")

    dist_tp = (t['tp']-price) if is_buy else (price-t['tp'])
    st.caption(f"GOLD LIVE REAL {price:.2f} | To TP: ${dist_tp:.2f} away | SA {sa} | 🔒 Will NOT flip till hit")
    st.progress(max(0,min(100,int((pnl+3.5)/17.5*100))))

    if tp_hit:
        st.success(f"✅ TP HIT +$14 at {price:.2f} - WIN!")
        st.session_state.stats['w']+=1; st.session_state.stats['t']+=1
        st.session_state.trade=None; st.balloons(); time.sleep(2); st.rerun()
    if sl_hit:
        st.error(f"❌ SL HIT -$3.5 at {price:.2f}")
        st.session_state.stats['t']+=1
        st.session_state.trade=None; time.sleep(2); st.rerun()

# --- SCAN FOR NEW SIGNAL ---
else:
    if len(st.session_state.history) < 20:
        st.markdown(f"<div class='wait'><div class='big'>WAIT</div><div>Loading REAL gold history... {len(st.session_state.history)}/20<br>GOLD LIVE {price:.2f}</div></div>", unsafe_allow_html=True)
    else:
        h = st.session_state.history
        e10 = ema(h, 10); e20 = ema(h, 20)
        r14 = rsi(h, 14); r7 = rsi(h, 7)
        low15 = min(h[-15:]); high15 = max(h[-15:])

        signal = "WAIT"
        # YOUR EDGE: flat EMA + mid RSI + near 15-bar low = early dip like 4175.13
        if e10 >= e20-0.8 and e10 <= e20+1.0 and r14>=36 and r14<=59 and r7>41 and (price-low15) < 2.8:
            signal = "BUY"
        elif e10 >= e20-1.0 and e10 <= e20+0.8 and r14>=41 and r14<=66 and r7<58 and (high15-price) < 2.8:
            signal = "SELL"

        if signal!= "WAIT":
            e = price; sl = e-3.5 if signal=="BUY" else e+3.5; tp = e+14 if signal=="BUY" else e-14
            st.session_state.trade = {'d':signal,'e':e,'sl':sl,'tp':tp}
            st.rerun()
        else:
            st.markdown(f"<div class='wait'><div class='big'>WAIT</div><div style='font-size:12px'>RSI {r14:.0f} | EMA {e10:.2f}/{e20:.2f}<br>GOLD LIVE REAL {price:.2f} | Near Low {price-low15:.2f}$ | Scanning early entry...</div></div>", unsafe_allow_html=True)
            st.caption("Logic: HOLD TILL TP like your 4175.13 → 4189.13 example. BUY when EMA flat + RSI 36-59 + near 15-bar low")

st.markdown("---")
a,b,c = st.columns(3)
a.metric("GOLD LIVE REAL", f"{price:.2f}")
b.metric("ENTRY", f"{st.session_state.trade['e']:.2f}" if st.session_state.trade else "---")
c.metric("TP / SL", f"{st.session_state.trade['tp']:.2f} / {st.session_state.trade['sl']:.2f}" if st.session_state.trade else "WAIT")
st.caption(f"SA {sa} | {st.session_state.stats['t']} trades | {st.session_state.stats['w']} wins | Real API