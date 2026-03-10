import requests, time
from datetime import datetime

BOT_TOKEN = "8197050727:AAHwO3EJufe60a990ZlilVkZaBocC_3xb_E"
CHAT_ID   = "8304161970"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})
    except:
        pass

def get_price():
    url = "https://fapi.binance.com/fapi/v1/ticker/price?symbol=XAUUSDT"
    r = requests.get(url)
    return float(r.json()["price"])

prev_price = None
send_telegram("📊 <b>بدأ إرسال تحديثات سعر الذهب كل دقيقة</b>")

while True:
    try:
        price = get_price()
        now = datetime.now().strftime("%H:%M:%S")
        diff_str = ""
        if prev_price:
            diff = price - prev_price
            diff_str = f"🟢 +{diff:.2f}" if diff > 0 else f"🔴 {diff:.2f}"
        else:
            diff_str = "➡️ 0.00"

        msg = (f"💰 <b>XAUUSDT</b>\n"
               f"السعر: <code>{price:.2f}</code>\n"
               f"التغير: <code>{diff_str}</code>\n"
               f"⏰ {now}")
        send_telegram(msg)
        prev_price = price

    except Exception as e:
        print(f"خطأ: {e}")

    time.sleep(60)
