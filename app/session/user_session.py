from algorithms import Queue
import asyncio
import session
import foxbit
import websockets

class UserSession(object):
  def __init__(self, chat_id):
    self.__id = chat_id
    self.__buffer = Queue()
    self.__state = session.State.START
    self.__callbackBuffer = None
    self.__fb = None
    # user login information
    self.__username = None

  def getBuffer(self):
    return self.__buffer

  async def listen(self, buffer):
    async with websockets.connect(foxbit.URI) as ws:
      self.__fb = foxbit.Foxbit(ws)

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

  def __sendManagerMessage(self, msg):
    self.__callbackBuffer.push({
      "from": "session",
      "data": {
        "id": self.__id,
        "message": msg
      }
    })

  def __isCriticalState(self):
    return self.__state in [session.State.WAITING_FOR_EMAIL, 
                            session.State.WAITING_FOR_PASSWORD]

  async def __handleCriticalInformation(self, msg):
    if self.__state == session.State.WAITING_FOR_EMAIL:
      self.__recvEmail(msg)
    elif self.__state == session.State.WAITING_FOR_PASSWORD:
      await self.__recvPassword(msg)

  # handle for askeds requests
  def __recvEmail(self, email):
    self.__username = email
    self.__state = session.State.WAITING_FOR_PASSWORD
    self.__sendManagerMessage(session.ASK_PASSWORD)

  async def __recvPassword(self, password):
    response = await self.__fb.authenticate(self.__username, password)

    if response["o"]["Authenticated"] == False:
      self.__state = session.State.START
      self.__sendManagerMessage(session.INVALID_EMAIL_OR_PASSWORD)
    else:
      self.__state = session.State.LOGGED
      self.__sendManagerMessage(session.LOGGED)

  async def __handleSessionCommand(self, msg):
    if msg == "/start":
      self.__sendManagerMessage(session.START)
    elif msg == "/login":
      self.__login()

  def __login(self):
    self.__state = session.State.WAITING_FOR_EMAIL
    self.__sendManagerMessage(session.ASK_EMAIL)
