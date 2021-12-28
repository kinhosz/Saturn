import telepot
import os
import telegram
import asyncio

async def render():
  bot = telepot.Bot(os.getenv('telegram_token'))
  tHandler = telegram.Handler(bot)
  
  receiver_task = asyncio.create_task(telegram.receiver(bot, tHandler.getBuffer()))
  handle_message_task = asyncio.create_task(tHandler.handle())

  await receiver_task
  await handle_message_task