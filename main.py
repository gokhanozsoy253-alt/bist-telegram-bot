import os
from flask import Flask, request
import requests
from analysis import analyze
from telegram.ext import ApplicationBuilder, CommandHandler

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

app = Flask(__name__)

# ---------- TELEGRAM BOT ----------

async def hisse(update, context):
    if not context.args:
        await update.message.reply_text("Kullanım: /hisse ASELS")
        return

    symbol = context.args[0].upper() + ".IS"
    result = analyze(symbol)

    if not result:
        await update.message.reply_text("Veri alınamadı")
        return

    text = f"""
📈 BIST HİSSE ANALİZİ

Hisse: {symbol}
Fiyat: {result['price']} TL
Puan: {result['score']}/100

Nedenler:
"""
    for r in result["reasons"]:
        text += f"• {r}\n"

    text += "\n⚠️ Yatırım tavsiyesi değildir."
    await update.message.reply_text(text)

bot_app = ApplicationBuilder().token(TOKEN).build()
bot_app.add_handler(CommandHandler("hisse", hisse))

# ---------- WEBHOOK ----------

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    symbol = data.get("ticker", "").replace("BIST:", "") + ".IS"

    result = analyze(symbol)
    if not result:
        return "OK", 200

    msg = f"""
🚨 CANLI SİNYAL

Hisse: {symbol}
Fiyat: {result['price']} TL
Puan: {result['score']}/100
"""
    for r in result["reasons"]:
        msg += f"• {r}\n"

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": msg}
    )

    return "OK", 200

# ---------- RUN ----------

if __name__ == "__main__":
    import threading

    threading.Thread(target=lambda: bot_app.run_polling()).start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
