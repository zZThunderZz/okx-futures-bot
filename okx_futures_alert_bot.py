import asyncio
import json
import os
import time
import aiohttp
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SYMBOLS = os.getenv("SYMBOLS", "BTC-USDT,ETH-USDT").split(',')
OI_THRESHOLD = float(os.getenv("OI_THRESHOLD", "2.0"))  # в %
INTERVAL = int(os.getenv("INTERVAL_SECONDS", "300"))

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

oi_cache = {}

async def get_open_interest(symbol):
    url = f"https://www.okx.com/api/v5/public/open-interest?instType=SWAP&instId={symbol}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return float(data['data'][0]['oi'])

async def check_open_interest():
    while True:
        for symbol in SYMBOLS:
            try:
                current_oi = await get_open_interest(symbol)
                last_oi = oi_cache.get(symbol)

                if last_oi is not None:
                    change = ((current_oi - last_oi) / last_oi) * 100
                    if abs(change) >= OI_THRESHOLD:
                        direction = "🔼 рост" if change > 0 else "🔻 падение"
                        msg = f"📊 Open Interest на {symbol} изменился на {change:.2f}% ({direction})"
                        await bot.send_message(TELEGRAM_CHAT_ID, msg)

                oi_cache[symbol] = current_oi

            except Exception as e:
                print(f"Ошибка при получении OI для {symbol}: {e}")

        await asyncio.sleep(INTERVAL)

async def main():
    await check_open_interest()

if __name__ == "__main__":
    asyncio.run(main())
