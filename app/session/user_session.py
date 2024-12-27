import asyncio
import json
import re

from app.algorithms import Queue
from app import session
from app import foxbit
from app import db

class UserSession(object):
  def __init__(self, chat_id):
    self._id = chat_id
    self._buffer = Queue()
    self._state = session.State.START
    self._callbackBuffer = None
    self._fb = None
    # user login information
    self._username = None
    # trade information
    self._trade = None
    self._tradeTask = None
    # temps values
    self._temp = []

  def getBuffer(self):
    return self._buffer

  def _clearTemp(self):
    self._temp = []

  def _restart(self):
    self._state = session.State.START
    self._buffer = Queue()
    self._trade = None
    self._tradeTask = None
    self._temp = []

  async def listen(self, buffer):
    self._fb = foxbit.Foxbit()

    self._callbackBuffer = buffer
    DELAY_FOR_WAIT_MESSAGES_IN_SECONDS = 0.1

    while True:
      buffer_sz = self._buffer.size()

      for i in range(buffer_sz):
        message = self._buffer.front()
        self._buffer.pop()
        await self._handleMsg(message)
      
      await asyncio.sleep(DELAY_FOR_WAIT_MESSAGES_IN_SECONDS)

  async def _handleMsg(self, message):
    if message["from"] == "telegram":
      await self._handleTelegramMessages(message["data"])
    elif message["from"] == "manager":
      await self._handleManagerMessages(message["data"])

  async def _handleTelegramMessages(self, message):
    if 'text' not in message.keys():
      return None

    msg = message['text']
    if self._isCriticalState():
      await self._handleCriticalInformation(msg)
    else:
      await self._handleSessionCommand(msg)

  def _sendManagerMessage(self, msg):
    self._callbackBuffer.push({
      "from": "session",
      "data": {
        "id": self._id,
        "message": msg
      }
    })

  def _assertLogged(self):
    if self._state != session.State.START:
      return True

    self._sendManagerMessage(session.WARNING_NOT_LOGGED)

  def _isCriticalState(self):
    return self._state in [session.State.WAITING_FOR_EMAIL, 
                            session.State.WAITING_FOR_PASSWORD,
                            session.State.WAITING_FOR_HISTORY_LIMIT,
                            session.State.WAITING_FOR_VALLEY,
                            session.State.WAITING_FOR_PROFIT]

  async def _handleCriticalInformation(self, msg):
    if self._state == session.State.WAITING_FOR_EMAIL:
      self._recvEmail(msg)
    elif self._state == session.State.WAITING_FOR_PASSWORD:
      await self._recvPassword(msg)
    elif self._state == session.State.WAITING_FOR_HISTORY_LIMIT:
      self._recvHistoryLimit(msg)
    elif self._state == session.State.WAITING_FOR_VALLEY:
      self._recvValley(msg)
    elif self._state == session.State.WAITING_FOR_PROFIT:
      self._recvProfit(msg)

  def _deletePassword(self, response):
    try:
      body = response["body"]
      body = json.loads(body)
      ro = body["o"]
      ro = json.loads(ro)
      ro["Password"] = "secret"
      ro = json.dumps(ro)
      body["o"] = ro
      body = json.dumps(body)
      response["body"] = body
    except:
      return None

  # log erros and set break state
  def _isResponseOk(self, response, password=False):
    if response["status"] == "Failed":
      self._restart()
      if password:
        self._deletePassword(response)

      self._sendManagerMessage(session.log_error(**response))
      return False
    else:
      return True

  # handle for askeds requests
  def _recvEmail(self, email):
    self._username = email
    self._state = session.State.WAITING_FOR_PASSWORD
    self._sendManagerMessage(session.ASK_PASSWORD)

  async def _recvPassword(self, password):
    response = await self._fb.authenticate(self._username, password)
    if not self._isResponseOk(response, password=True):
      return None

    if response["o"]["Authenticated"] == False:
      self._state = session.State.START
      self._sendManagerMessage(session.INVALID_EMAIL_OR_PASSWORD)
    else:
      self._state = session.State.LOGGED
      self._sendManagerMessage(session.LOGGED)

  def _recvHistoryLimit(self, limit):
    if not limit.isdigit():
      self._state = session.State.LOGGED
      self._sendManagerMessage(session.INVALID_HISTORY_LIMIT)
    else:
      self._temp.append(int(limit))
      self._state = session.State.WAITING_FOR_VALLEY
      self._sendManagerMessage(session.ASK_VALLEY)

  def _recvValley(self, valley):
    if re.fullmatch('0\.\d+', valley) == None:
      self._state = session.State.LOGGED
      self._sendManagerMessage(session.INVALID_VALLEY)
    else:
      f_valley = float(valley)
      self._temp.append(f_valley)
      self._state = session.State.WAITING_FOR_PROFIT
      self._sendManagerMessage(session.ASK_PROFIT)

  def _recvProfit(self, profit):
    if re.fullmatch('0\.\d+', profit) == None:
      self._state = session.State.LOGGED
      self._sendManagerMessage(session.INVALID_PROFIT)
    else:
      f_profit = float(profit)
      self._createTrade(self._temp[0], self._temp[1], f_profit)
      self._clearTemp()
      self._state = session.State.TRADE_CREATED
      self._sendManagerMessage(session.TRADE_CREATED)

  # handle for commands
  async def _handleSessionCommand(self, msg):
    if msg == "/start":
      self._sendManagerMessage(session.START)
    elif msg == "/login":
      self._login()
    elif msg == "/trade_start":
      await self._startTrade()

  def _login(self):
    if self._state != session.State.START:
      self._sendManagerMessage(session.WARNING_ALREADY_LOGGED)
      return None

    self._state = session.State.WAITING_FOR_EMAIL
    self._sendManagerMessage(session.ASK_EMAIL)

  async def _startTrade(self):
    success = await self._authenticate()

    if not success:
      return None

    response = await self._getCurrencyValue()
    price = response["Ask"]
    self._sendManagerMessage(session.current_price(price))

    order_id = db.insert("orders", ["ask", "bid"], [response["Ask"], response["Bid"]])[0][0]

    accountId = await self._getAccountId()
    clientOrderId = await self._getClientOrderId(accountId)

    response = await self._fb.buy(accountId, clientOrderId)
    if not self._isResponseOk(response):
      return None

    if response["o"]["status"] == "Accepted":
      self._sendManagerMessage(session.currency_buyed(price))
    else:
      self._sendManagerMessage(session.log_error(description="Erro ao comprar moeda",
                                                          path="user_session._tradeLife",
                                                          body=json.dumps(response)))
      return None

    user_id = db.find_equal("users", "chat_id", str(self._id), ["id"])[0][0]
    db.insert("trades", ["user_id", "order_bought_id"], [user_id, order_id])

  def _createTrade(self, limit, valley, profit):
    self._trade = foxbit.Trade(limit, valley, profit)
    self._tradeTask = asyncio.create_task(self._tradeLife())

  async def _tradeLife(self):
    DELAY_FOR_GET_CURRENCY_VALUE_IN_SECONDS = 600
    buyed = False

    buyedFor = None

    # waiting for buy
    while not buyed:
      response = await self._getCurrencyValue()
      price = response["Ask"]
      if self._trade.addPrice(price):
        buyedFor = price
        self._trade.lockPrice(price)
        buyed = True
        self._sendManagerMessage(session.current_price(price))
      else:
        self._sendManagerMessage(session.current_price(price))
      await asyncio.sleep(DELAY_FOR_GET_CURRENCY_VALUE_IN_SECONDS)

    response = await self._fb.getAccountId()
    if not self._isResponseOk(response):
      return None
    
    accountId = response["data"]

    response = await self._fb.getClientOrderId(accountId)
    if not self._isResponseOk(response):
      return None

    clientOrderId = response["data"]

    response = await self._fb.buy(accountId, clientOrderId)
    if not self._isResponseOk(response):
      return None

    if response["o"]["status"] == "Accepted":
      self._sendManagerMessage(session.currency_buyed(buyedFor))
    else:
      self._restart()
      self._sendManagerMessage(session.log_error(description="Erro ao comprar moeda",
                                                          path="user_session._tradeLife",
                                                          body=json.dumps(response)))
      return None

    sold = False
    soldFor = None
    # waiting for sell
    while not sold:
      response = await self._getCurrencyValue()
      price = response["Bid"]
      if self._trade.checkProfit(price):
        sold = True
        soldFor = price
        self._sendManagerMessage(session.current_price(price))
      else:
        self._sendManagerMessage(session.current_price(price))
      await asyncio.sleep(DELAY_FOR_GET_CURRENCY_VALUE_IN_SECONDS)

    response = await self._fb.sell(accountId, clientOrderId)
    if not self._isResponseOk(response):
      return None

    if response["o"]["status"] == "Accepted":
      self._sendManagerMessage(session.currency_sold(buyedFor, soldFor))
    else:
      self._restart()
      self._sendManagerMessage(session.log_error(description="Erro ao vender moeda",
                                                          path="user_session._tradeLife",
                                                          body=json.dumps(response)))
  
  async def _getCurrencyValue(self):
    response = await self._fb.getTickerHistory()
    if not self._isResponseOk(response):
      return None

    return response["o"]

  # handle manager commands and operations
  async def _handleManagerMessages(self, request):
    if request["operation"] == "sell_trade":
      await self._sellTrade(request["trade_id"], request["order_id"])
  
  # sell a currency and close trade
  async def _sellTrade(self, trade_id, order_id):
    await self._authenticate()

    accountId = await self._getAccountId()
    clientOrderId = await self._getClientOrderId(accountId)

    order_bought_id = db.find_equal("trades", "id", trade_id, ["order_bought_id"])[0][0]
    bought = db.find_equal("orders", "id", order_bought_id, ["ask"])[0][0]
    sold = db.find_equal("orders", "id", order_id, ["bid"])[0][0]

    response = await self._fb.sell(accountId, clientOrderId)
    if not self._isResponseOk(response):
      return None

    if response["o"]["status"] == "Accepted":
      self._sendManagerMessage(session.currency_sold(bought, sold))
    else:
      self._sendManagerMessage(session.log_error(description="Erro ao vender moeda",
                                                  path="user_session._tradeLife",
                                                  body=json.dumps(response),
                                                  status=response["o"]["status"]))
      return None

    db.update("trades", trade_id, ["order_sold_id"], [order_id])

  async def _getAccountId(self):
    response = await self._fb.getAccountId()
    if not self._isResponseOk(response):
      return None
    
    return response["data"]

  async def _getClientOrderId(self, accountId):
    response = await self._fb.getClientOrderId(accountId)
    if not self._isResponseOk(response):
      return None

    return response["data"]

  async def _authenticate(self):
    user_credentials = db.find_equal("users", "chat_id", str(self._id), ["email", "encrypted_password"])

    if len(user_credentials) == 0:
      self._sendManagerMessage(session.accountNotFound())
      return False

    email = user_credentials[0][0]
    password = user_credentials[0][1]

    response = await self._fb.authenticate(email, password)
    if not self._isResponseOk(response, password=True):
      return False

    if response["o"]["Authenticated"] == False:
      self._sendManagerMessage(session.INVALID_EMAIL_OR_PASSWORD)
      return False
    
    return True
