import asyncio

from app.algorithms import Queue
from app import telegram
from app import session
from app import foxbit
from app import db

class Manager(object):
  def __init__(self):
    self._serverBuffer = None
    self._buffer = Queue()
    self._activeSessions = {}

  async def listen(self):
    DELAY_FOR_WAIT_MESSAGES_IN_SECONDS = 0.1

    while True:
      buffer_sz = self._buffer.size()

      for i in range(buffer_sz):
        message = self._buffer.front()
        self._buffer.pop()
        await self._handleResponse(message)
      
      await asyncio.sleep(DELAY_FOR_WAIT_MESSAGES_IN_SECONDS)

  def getBuffer(self):
    return self._buffer

  def setServerBuffer(self, sb):
    self._serverBuffer = sb

  def _sendToServer(self, chat_id, message):
    self._serverBuffer.push({
      "from": "manager",
      "data": {
        "id": chat_id,
        "message": message
      }
    })

  async def _handleResponse(self, response):
    if response["from"] == "telegram":
      await self._dispatch(response["data"])
    elif response["from"] == "session":
      self._sendToServer(response["data"]["id"], response["data"]["message"])
    elif response["from"] == "foxbit":
      self._foxbitService(response["data"])

  async def _dispatch(self, message):
    if 'message' in message.keys():
      message = message['message']
    else:
      return None

    if message['chat']['type'] != 'private':
      await self._sender(message['chat']['id'], telegram.ONLY_PRIVATE_CHAT)
      return None

    chat_id = message['chat']['id']

    request = {
      "from": "telegram",
      "data": message
    }
    self._requestToSession(chat_id, request)
  
  def _requestToSession(self, chat_id, request):
    if chat_id not in self._activeSessions.keys():
      self._createSession(chat_id)
    
    self._activeSessions[chat_id]["buffer"].push(request)

  def _createSession(self, chat_id):
    uSession = session.UserSession(chat_id)
    buffer = uSession.getBuffer()
    task = asyncio.create_task(uSession.listen(self.getBuffer()))

    self._activeSessions[chat_id] = {
      "session": uSession,
      "buffer": buffer,
      "task": task
    }

  def _foxbitService(self, request):
    if request["operation"] == "sell_trade":
      self._foxbitSellTrade(request["order_id"], request["trade_id"])

  def _foxbitSellTrade(self, order_id, trade_id):
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

    self._requestToSession(chat_id, request)
