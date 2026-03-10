import requests, time, numpy as np
from datetime import datetime

BOT_TOKEN = "8197050727:AAHwO3EJufe60a990ZlilVkZaBocC_3xb_E"
CHAT_ID   = "8304161970"

DOJI_SIZE = 0.1
STOCH_LEN = 14
OB_LEVEL  = 60
OS_LEVEL  = 40

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})
    except:
        pass

def get_candles():
    url = "https://api.binance.com/api/v3/klines?symbol=XAUUSDT&interval=5m&limit=100"
    r = requests.get(url)
    data = r.json()
    o = np.array([float(x[1]) for x in data])
    h = np.array([float(x[2]) for x in data])
    l = np.array([float(x[3]) for x in data])
    c = np.array([float(x[4]) for x in data])
    return o, h, l, c

def heikin_ashi(o, h, l, c):
    ha_c = (o + h + l + c) / 4
    ha_o = np.zeros(len(o))
    ha_o[0] = (o[0] + c[0]) / 2
    for i in range(1, len(o)):
        ha_o[i] = (ha_o[i-1] + ha_c[i-1]) / 2
    ha_h = np.maximum(h, np.maximum(ha_o, ha_c))
    ha_l = np.minimum(l, np.minimum(ha_o, ha_c))
    return ha_o, ha_h, ha_l, ha_c

def stoch(ha_h, ha_l, ha_c):
    k = np.zeros(len(ha_c))
    for i in range(STOCH_LEN, len(ha_c)):
        lo = np.min(ha_l[i-STOCH_LEN:i])
        hi = np.max(ha_h[i-STOCH_LEN:i])
        k[i] = ((ha_c[i] - lo) / (hi - lo)) * 100 if hi != lo else 50
    return k

prev_signal = None
print("✅ DXB Bot يعمل 24/7")
send_telegram("✅ <b>DXB 1.3 Bot يعمل 24/7!</b>\nيراقب XAUUSDT · 5 دقائق · Heikin Ashi")

while True:
    try:
        o, h, l, c = get_candles()
        ha_o, ha_h, ha_l, ha_c = heikin_ashi(o, h, l, c)
        k = stoch(ha_h, ha_l, ha_c)
        now = datetime.now().strftime("%H:%M:%S")
        price = ha_c[-2]

        last_signal = None
        for i in range(4, len(ha_c)-1):
            body  = abs(ha_c[i-2] - ha_o[i-2])
            rng   = ha_h[i-2] - ha_l[i-2]
            is_doji = rng > 0 and body <= rng * DOJI_SIZE
            stoch_buy  = k[i-2] <= OS_LEVEL or k[i-3] <= OS_LEVEL
            stoch_sell = k[i-2] >= OB_LEVEL or k[i-3] >= OB_LEVEL
            if is_doji and stoch_buy  and ha_c[i-1] > ha_h[i-2]:
                last_signal = ('buy', i)
            elif is_doji and stoch_sell and ha_c[i-1] < ha_l[i-2]:
                last_signal = ('sell', i)

        if last_signal:
            sig_key = f"{last_signal[0]}_{last_signal[1]}"
            if sig_key != prev_signal:
                prev_signal = sig_key
                emoji = "🟢" if last_signal[0] == "buy" else "🔴"
                label = "شراء BUY" if last_signal[0] == "buy" else "بيع SELL"
                msg = (f"{emoji} <b>إشارة {label}</b>\n\n"
                       f"💰 السعر: <code>{price:.2f}</code>\n"
                       f"📊 Stoch: <code>{k[-2]:.1f}</code>\n"
                       f"⏰ {now}")
                send_telegram(msg)
                print(f"[{now}] ✅ {label} — {price:.2f}")
        
        print(f"[{now}] مراقبة... {price:.2f} | K: {k[-2]:.1f}")

    except Exception as e:
        print(f"خطأ: {e}")

    time.sleep(60)
