from algorithms import Queue
import asyncio
import session

class UserSession(object):
  def __init__(self, chat_id):
    self.__id = chat_id
    self.__buffer = Queue()
    self.__state = session.State.START
    self.__callbackBuffer = None

  def getBuffer(self):
    return self.__buffer

  async def listen(self, buffer):
    self.__callbackBuffer = buffer
    DELAY_FOR_WAIT_MESSAGES_IN_SECONDS = 0.1

    while True:
      buffer_sz = self.__buffer.size()

      for i in range(buffer_sz):
        message = self.__buffer.front()
        self.__buffer.pop()
        await self.__handleMsg(message)
      
      await asyncio.sleep(DELAY_FOR_WAIT_MESSAGES_IN_SECONDS)

  async def __handleMsg(self, message):
    if message["from"] == "telegram":
      await self.__handleTelegramMessages(message["data"])

  async def __handleTelegramMessages(self, response):
    if 'text' not in response.keys():
      return None

    msg = response['text']
    if self.__isCriticalState():
      await self.__handleCriticalInformation(msg)
    else:
      await self.__handleSessionCommand(msg)

  def __isCriticalState(self):
    return self.__state in [session.State.WAITING_FOR_EMAIL, 
                            session.State.WAITING_FOR_PASSWORD]

  async def __handleCriticalInformation(self, msg):
    pass

  def __sendManagerMessage(self, msg):
    self.__callbackBuffer.push({
      "from": "session",
      "data": {
        "id": self.__id,
        "message": msg
      }
    })

  async def __handleSessionCommand(self, msg):
    if msg == "/start":
      self.__sendManagerMessage(session.START)