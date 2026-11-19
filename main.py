import asyncio
asyncio.set_event_loop(asyncio.new_event_loop())import os import json import urllib.request import logging from telegram import Update from telegram.ext import ( Application, CommandHandler, ContextTypes )
logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
def get_market_data(symbol="BTCUSDT"): url = ( "https://api.binance.com/api/v3/klines" f"?symbol={symbol}&interval=15m&limit=100" )
req = urllib.request.Request(
    url,
    headers={"User-Agent": "Mozilla/5.0"}
)

with urllib.request.urlopen(req, timeout=15) as response:
    data = json.loads(response.read())

return [float(candle[4]) for candle in data]
def ema(values, period): result = sum(values[:period]) / period multiplier = 2 / (period + 1)
for price in values[period:]:
    result = (
        price * multiplier
        + result * (1 - multiplier)
    )

return result
def rsi(values, period=14): changes = [ values[i] - values[i - 1] for i in range(1, len(values)) ]
gains = [max(x, 0) for x in changes]
losses = [max(-x, 0) for x in changes]

avg_gain = sum(gains[-period:]) / period
avg_loss = sum(losses[-period:]) / period

if avg_loss == 0:
    return 100

rs = avg_gain / avg_loss
return 100 - (100 / (1 + rs))
def analyze(symbol): prices = get_market_data(symbol)
current = prices[-1]
rsi_value = rsi(prices)

ema_fast = ema(prices, 12)
ema_slow = ema(prices, 26)

macd_signal = (
    "صعودی" if ema_fast > ema_slow else "نزولی"
)

if rsi_value < 30 and ema_fast > ema_slow:
    signal = "🟢 خرید احتمالی"
elif rsi_value > 70 and ema_fast < ema_slow:
    signal = "🔴 فروش احتمالی"
else:
    signal = "🟡 انتظار"

return (
    f"📊 تحلیل {symbol}\n\n"
    f"💰 قیمت: {current}\n"
    f"📈 RSI: {rsi_value:.2f}\n"
    f"📉 وضعیت MACD: {macd_signal}\n"
    f"📊 EMA 12: {ema_fast:.4f}\n"
    f"📊 EMA 26: {ema_slow:.4f}\n\n"
    f"🎯 نتیجه: {signal}\n\n"
    "⚠️ این تحلیل سیگنال قطعی نیست."
)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): keyboard = ( "🤖 به ربات Saeid AI Trader خوش آمدید!\n\n" "دستورات ربات:\n" "/analyze BTCUSDT - تحلیل بیت کوین\n" "/analyze ETHUSDT - تحلیل اتریوم\n" "/markets - نمایش بازارها\n" "/help - راهنما\n\n" "📊 تحلیل بازار و سیگنال آزمایشی" )
await update.message.reply_text(keyboard)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text( "برای تحلیل ارز دیجیتال بنویسید:\n" "/analyze BTCUSDT\n\n" "مثال:\n" "/analyze ETHUSDT" )
async def markets(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text( "بازارهای قابل تحلیل در نسخه فعلی:\n" "BTCUSDT\n" "ETHUSDT\n" "BNBUSDT\n" "SOLUSDT\n\n" "منبع اطلاعات: Binance" )
async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE): symbol = "BTCUSDT"
if context.args:
    symbol = context.args[0].upper()

await update.message.reply_text(
    "⏳ در حال تحلیل بازار..."
)

try:
    result = await __import__("asyncio").to_thread(
        analyze, symbol
    )
    await update.message.reply_text(result)

except Exception as error:
    logging.exception("Analysis failed")
    await update.message.reply_text(
        "خطا در دریافت اطلاعات بازار. دوباره تلاش کنید."
    )
def main(): if not TOKEN: raise RuntimeError( "TELEGRAM_BOT_TOKEN is not configured" )
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("markets", markets))
app.add_handler(CommandHandler("analyze", analyze_command))

print("Saeid AI Trader is running...")

app.run_polling()
if name == "main": main()
