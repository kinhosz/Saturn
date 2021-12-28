from algorithms import Queue
from session import UserSession
import telegram
import asyncio

class Handler(object):
  def __init__(self, tbot):
    self.__tbot = tbot
    self.__buffer = Queue()
    self.__activeSessions = {}

  def getBuffer(self):
    return self.__buffer

  def __createSession(self, message):
    uSession = UserSession(self.__tbot, message['chat']['id'])
    uSession.handleMsg(message)

    self.__activeSessions[message['chat']['id']] = uSession

  async def __handleMsg(self, update):
    if 'message' in update.keys():
      message = update['message']
    elif 'edited_message' in update.keys():
      message = update['edited_message']
    else:
      return None

    if message['chat']['type'] != 'private':
      await telegram.sender(self.__tbot, message['chat']['id'], telegram.ONLY_PRIVATE_CHAT)
      return None

    chat_id = message['chat']['id']

    if chat_id not in self.__activeSessions.keys():
      self.__createSession(message)
    else:
      self.__activeSessions[chat_id].handleMsg(message)

  async def handle(self):
    DELAY_FOR_WAIT_MESSAGES_IN_SECONDS = 1

    while True:
      buffer_sz = self.__buffer.size()

      for i in range(buffer_sz):
        message = self.__buffer.front()
        self.__buffer.pop()
        await self.__handleMsg(message)
      
      await asyncio.sleep(DELAY_FOR_WAIT_MESSAGES_IN_SECONDS)
