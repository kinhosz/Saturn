from algorithms import Queue
import telegram
import session
import asyncio
import foxbit
import db

class Manager(object):
  def __init__(self):
    self.__serverBuffer = None
    self.__buffer = Queue()
    self.__activeSessions = {}

  async def listen(self):
    DELAY_FOR_WAIT_MESSAGES_IN_SECONDS = 0.1

    while True:
      buffer_sz = self.__buffer.size()

      for i in range(buffer_sz):
        message = self.__buffer.front()
        self.__buffer.pop()
        await self.__handleResponse(message)
      
      await asyncio.sleep(DELAY_FOR_WAIT_MESSAGES_IN_SECONDS)

  def getBuffer(self):
    return self.__buffer

  def setServerBuffer(self, sb):
    self.__serverBuffer = sb

  def __sendToServer(self, chat_id, message):
    self.__serverBuffer.push({
      "from": "manager",
      "data": {
        "id": chat_id,
        "message": message
      }
    })

  async def __handleResponse(self, response):
    if response["from"] == "telegram":
      await self.__dispatch(response["data"])
    elif response["from"] == "session":
      self.__sendToServer(response["data"]["id"], response["data"]["message"])
    elif response["from"] == "foxbit":
      self.__foxbitService(response["data"])
    elif response["from"] == "search21":
      self.__search21(response["data"])

  async def __dispatch(self, message):
    if 'message' in message.keys():
      message = message['message']
    else:
      return None

    if message['chat']['type'] != 'private':
      await self.__sender(message['chat']['id'], telegram.ONLY_PRIVATE_CHAT)
      return None

    chat_id = message['chat']['id']

    request = {
      "from": "telegram",
      "data": message
    }
    self.__requestToSession(chat_id, request)
  
  def __requestToSession(self, chat_id, request):
    if chat_id not in self.__activeSessions.keys():
      self.__createSession(chat_id)
    
    self.__activeSessions[chat_id]["buffer"].push(request)

  def __createSession(self, chat_id):
    uSession = session.UserSession(chat_id)
    buffer = uSession.getBuffer()
    task = asyncio.create_task(uSession.listen(self.getBuffer()))

    self.__activeSessions[chat_id] = {
      "session": uSession,
      "buffer": buffer,
      "task": task
    }

  def __foxbitService(self, request):
    if request["operation"] == "sell_trade":
      self.__foxbitSellTrade(request["order_id"], request["trade_id"])

  def __foxbitSellTrade(self, order_id, trade_id):
    user_id = db.find_equal("trades", "id", trade_id, ["user_id"])[0][0]
    chat_id = db.find_equal("users", "id", user_id, ["chat_id"])[0][0]

    request = {
      "from": "manager",
      "data": {
        "operation": "sell_trade",
        "order_id": order_id,
        "trade_id": trade_id
      }
    }

    self.__requestToSession(chat_id, request)

  def __search21(self, message):
    user_id = db.find_equal("users", "email", "scruz.josecarlos@gmail.com", ["id"])[0][0]
    chat_id = db.find_equal("users", "id", user_id, ["chat_id"])[0][0]

    request = {
      "from": "manager",
      "data": {
        "id": chat_id,
        "message": message
      }
    }

    self.__serverBuffer.push(request)