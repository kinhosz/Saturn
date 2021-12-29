from algorithms import Queue
import telegram
import session
import asyncio

class Manager(object):
  def __init__(self):
    self.__sender = None
    self.__buffer = Queue()
    self.__activeSessions = {}

  def setSender(self, sender):
    self.__sender = sender

  async def listen(self):
    DELAY_FOR_WAIT_MESSAGES_IN_SECONDS = 1

    while True:
      buffer_sz = self.__buffer.size()

      for i in range(buffer_sz):
        message = self.__buffer.front()
        self.__buffer.pop()
        await self.__dispatch(message)
      
      await asyncio.sleep(DELAY_FOR_WAIT_MESSAGES_IN_SECONDS)

  def getBuffer(self):
    return self.__buffer

  async def __dispatch(self, message):
    if 'message' in message.keys():
      message = message['message']
    else:
      return None

    if message['chat']['type'] != 'private':
      await self.__sender(message['chat']['id'], telegram.ONLY_PRIVATE_CHAT)
      return None

    chat_id = message['chat']['id']

    if chat_id not in self.__activeSessions.keys():
      self.__createSession(chat_id)

    self.__activeSessions[chat_id]["buffer"].push(message)

  def __callback(self, msg):
    pass

  def __createSession(self, chat_id):
    uSession = session.UserSession(chat_id)
    uSession.setCallback(self.__callback)
    buffer = uSession.getBuffer()
    task = asyncio.create_task(uSession.listen())

    self.__activeSessions[chat_id] = {
      "session": uSession,
      "buffer": buffer,
      "task": task
    }