import telepot
import asyncio
import os
from app.algorithms import Queue

class TServer(object):
  def __init__(self):
    self._tbot = telepot.Bot(os.getenv('telegram_token'))
    self._buffer = Queue()

  async def listenTelegram(self, buffer):
    DELAY_FOR_RECEIVE_MESSAGES_IN_SECONDS = 0.5

    current_id = 0
    response = self._tbot.getUpdates()

    if len(response) > 0:
      current_id = response[-1]['update_id'] + 1

    while True:
      response = self._tbot.getUpdates(offset = current_id)
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
