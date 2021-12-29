import telepot
import asyncio

class TServer(object):
  def __init__(self):
    self.__tbot = telepot.Bot(os.getenv('telegram_token'))

  async def listen(self, buffer):
    DELAY_FOR_RECEIVE_MESSAGES_IN_SECONDS = 1

    current_id = 0
    response = tbot.getUpdates()

    if len(response) > 0:
      current_id = response[-1]['update_id'] + 1

    while True:
      response = self.__tbot.getUpdates(offset = current_id)
      for m in response:
        current_id = m['update_id'] + 1
        buffer.push(m)
      
      await asyncio.sleep(DELAY_FOR_RECEIVE_MESSAGES_IN_SECONDS)


  def getSender(self):
    return self.__sender

  async def __sender(self, chat_id, message):
    DELAY_FOR_SEND_MESSAGE_TO_CHAT_IN_SECONDS = 3
    await asyncio.sleep(DELAY_FOR_SEND_MESSAGE_TO_CHAT_IN_SECONDS)
    self.__tbot.send(chat_id, message)