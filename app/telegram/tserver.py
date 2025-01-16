import telepot
import asyncio
import os
from app.algorithms import Queue
from app.constant import env_name

class TServer(object):
  def __init__(self):
    self._tbot = None
    self._buffer = Queue()

    if env_name() == 'production':
      self._tbot = telepot.Bot(os.getenv('TELEGRAM_TOKEN'))
    else:
      self._tbot = telepot.Bot(os.getenv('TELEGRAM_TOKEN_DEV'))

  async def getUpdates(self, offset=None):
    while 1:
      try:
        response = self._tbot.getUpdates(offset)
        break
      except Exception as e:
        print(f"An error occured when getting telegram response\nError: {e}")
        await asyncio.sleep(60)
    return response

  async def listenTelegram(self, buffer):
    DELAY_FOR_RECEIVE_MESSAGES_IN_SECONDS = 0.5

    current_id = 0
    response = await self.getUpdates()

    if len(response) > 0:
      current_id = response[-1]['update_id'] + 1

    while True:
      response = await self.getUpdates(offset = current_id)
      for m in response:
        current_id = m['update_id'] + 1
        response = {
          "from": "telegram",
          "data": m
        }
        buffer.push(response)
      
      await asyncio.sleep(DELAY_FOR_RECEIVE_MESSAGES_IN_SECONDS)

  async def listenBuffer(self):
    DELAY_FOR_WAIT_MESSAGES_IN_SECONDS = 0.5

    while True:
      buffer_sz = self._buffer.size()

      for i in range(buffer_sz):
        message = self._buffer.front()
        self._buffer.pop()
        await self._handleResponse(message)

      await asyncio.sleep(DELAY_FOR_WAIT_MESSAGES_IN_SECONDS)

  async def _handleResponse(self, response):
    if response['from'] == 'manager':
      await self._sender(response['data']['id'], response['data']['message'])
    elif response['from'] == 'foxbit':
      await self._sender(response['data']['id'], response['data']['message'])

  def getBuffer(self):
    return self._buffer

  async def _sender(self, chat_id, message):
    DELAY_FOR_SEND_MESSAGE_TO_CHAT_IN_SECONDS = 0.1
    await asyncio.sleep(DELAY_FOR_SEND_MESSAGE_TO_CHAT_IN_SECONDS)
    self._tbot.sendMessage(chat_id, message)
