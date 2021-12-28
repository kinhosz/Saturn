import asyncio

async def sender(tbot, userId, message):
  DELAY_FOR_SEND_MESSAGE_TO_CHAT_IN_SECONDS = 3

  await asyncio.sleep(DELAY_FOR_SEND_MESSAGE_TO_CHAT_IN_SECONDS)
  tbot.sendMessage(userId, message)