from algorithms import Queue
import asyncio

class UserSession(object):
  def __init__(self, chat_id):
    self.__id = chat_id
    self.__callback = None
    self.__buffer = Queue()
    self.__state = 0

  def setCallback(self, callback):
    self.__callback = callback

  def getBuffer(self):
    return self.__buffer

  async def listen(self):
    DELAY_FOR_WAIT_MESSAGES_IN_SECONDS = 1

    while True:
      buffer_sz = self.__buffer.size()

      for i in range(buffer_sz):
        message = self.__buffer.front()
        self.__buffer.pop()
        await self.__handleMsg(message)
      
      await asyncio.sleep(DELAY_FOR_WAIT_MESSAGES_IN_SECONDS)

  async def __handleMsg(self, message):
    if 'text' not in message.keys():
      return None

    print("-------------------------------")
    print("received:", message['text'])