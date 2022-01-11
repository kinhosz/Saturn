from algorithms import Queue
import asyncio
import session
import foxbit
import websockets
import re

class UserSession(object):
  def __init__(self, chat_id):
    self.__id = chat_id
    self.__buffer = Queue()
    self.__state = session.State.START
    self.__callbackBuffer = None
    self.__fb = None
    # user login information
    self.__username = None
    # trade information
    self.__trade = None
    self.__tradeTask = None
    # temps values
    self.__temp = []

  def getBuffer(self):
    return self.__buffer

  def __clearTemp(self):
    self.__temp = []

  def __restart(self):
    self.__state = session.State.START
    self.__buffer = Queue()
    self.__trade = None
    self.__tradeTask = None
    self.__temp = []

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

  def __assertLogged(self):
    if self.__state != session.State.START:
      return True

    self.__sendManagerMessage(session.WARNING_NOT_LOGGED)

  def __isCriticalState(self):
    return self.__state in [session.State.WAITING_FOR_EMAIL, 
                            session.State.WAITING_FOR_PASSWORD,
                            session.State.WAITING_FOR_HISTORY_LIMIT,
                            session.State.WAITING_FOR_VALLEY,
                            session.State.WAITING_FOR_PROFIT]

  async def __handleCriticalInformation(self, msg):
    if self.__state == session.State.WAITING_FOR_EMAIL:
      self.__recvEmail(msg)
    elif self.__state == session.State.WAITING_FOR_PASSWORD:
      await self.__recvPassword(msg)
    elif self.__state == session.State.WAITING_FOR_HISTORY_LIMIT:
      self.__recvHistoryLimit(msg)
    elif self.__state == session.State.WAITING_FOR_VALLEY:
      self.__recvValley(msg)
    elif self.__state == session.State.WAITING_FOR_PROFIT:
      self.__recvProfit(msg)
      
  # log erros and set break state
  def __isResponseOk(self, response):
    if response["status"] == "Failed":
      self.__restart()
      self.__sendManagerMessage(session.log_error(**response))
      return False
    else:
      return True

  # handle for askeds requests
  def __recvEmail(self, email):
    self.__username = email
    self.__state = session.State.WAITING_FOR_PASSWORD
    self.__sendManagerMessage(session.ASK_PASSWORD)

  async def __recvPassword(self, password):
    response = await self.__fb.authenticate(self.__username, password)
    if not self.__isResponseOk(response):
      return None

    if response["o"]["Authenticated"] == False:
      self.__state = session.State.START
      self.__sendManagerMessage(session.INVALID_EMAIL_OR_PASSWORD)
    else:
      self.__state = session.State.LOGGED
      self.__sendManagerMessage(session.LOGGED)

  def __recvHistoryLimit(self, limit):
    if not limit.isdigit():
      self.__state = session.State.LOGGED
      self.__sendManagerMessage(session.INVALID_HISTORY_LIMIT)
    else:
      self.__temp.append(int(limit))
      self.__state = session.State.WAITING_FOR_VALLEY
      self.__sendManagerMessage(session.ASK_VALLEY)

  def __recvValley(self, valley):
    if re.fullmatch('0\.\d+', valley) == None:
      self.__state = session.State.LOGGED
      self.__sendManagerMessage(session.INVALID_VALLEY)
    else:
      f_valley = float(valley)
      self.__temp.append(f_valley)
      self.__state = session.State.WAITING_FOR_PROFIT
      self.__sendManagerMessage(session.ASK_PROFIT)

  def __recvProfit(self, profit):
    if re.fullmatch('0\.\d+', profit) == None:
      self.__state = session.State.LOGGED
      self.__sendManagerMessage(session.INVALID_PROFIT)
    else:
      f_profit = float(profit)
      self.__createTrade(self.__temp[0], self.__temp[1], f_profit)
      self.__clearTemp()
      self.__state = session.State.TRADE_CREATED
      self.__sendManagerMessage(session.TRADE_CREATED)

  # handle for commands
  async def __handleSessionCommand(self, msg):
    if msg == "/start":
      self.__sendManagerMessage(session.START)
    elif msg == "/login":
      self.__login()
    elif msg == "/trade_start":
      self.__startTrade()

  def __login(self):
    if self.__state != session.State.START:
      self.__sendManagerMessage(session.WARNING_ALREADY_LOGGED)
      return None

    self.__state = session.State.WAITING_FOR_EMAIL
    self.__sendManagerMessage(session.ASK_EMAIL)

  def __startTrade(self):
    if not self.__assertLogged():
      return None

    self.__state = session.State.WAITING_FOR_HISTORY_LIMIT
    self.__sendManagerMessage(session.ASK_HISTORY_LIMIT)

  def __createTrade(self, limit, valley, profit):
    self.__trade = foxbit.Trade(limit, valley, profit)
    self.__tradeTask = asyncio.create_task(self.__tradeLife())

  async def __tradeLife(self):
    DELAY_FOR_GET_CURRENCY_VALUE_IN_SECONDS = 600
    buyed = False

    buyedFor = None

    # waiting for buy
    while not buyed:
      response = await self.__getCurrencyValue()
      price = response["Ask"]
      if self.__trade.addPrice(price):
        buyedFor = price
        self.__trade.lockPrice(price)
        buyed = True
        self.__sendManagerMessage(session.current_price(price))
      else:
        self.__sendManagerMessage(session.current_price(price))
      await asyncio.sleep(DELAY_FOR_GET_CURRENCY_VALUE_IN_SECONDS)

    response = await self.__fb.getAccountId()
    if not self.__isResponseOk(response):
      return None
    
    accountId = response["data"]

    response = await self.__fb.getClientOrderId(accountId)
    if not self.__isResponseOk(response):
      return None

    clientOrderId = response["data"]

    response = await self.__fb.buy(accountId, clientOrderId)
    if not self.__isResponseOk(response):
      return None

    if response["o"]["status"] == "Accepted":
      self.__sendManagerMessage(session.currency_buyed(buyedFor))
    else:
      self.__restart()
      self.__sendManagerMessage(session.message.log_error(description="Erro ao comprar moeda",
                                                          path="user_session.__tradeLife",
                                                          body=json.dumps(response)))
      return None

    sold = False
    soldFor = None
    # waiting for sell
    while not sold:
      response = await self.__getCurrencyValue()
      price = response["Bid"]
      if self.__trade.checkProfit(price):
        sold = True
        soldFor = price
        self.__sendManagerMessage(session.current_price(price))
      else:
        self.__sendManagerMessage(session.current_price(price))
      await asyncio.sleep(DELAY_FOR_GET_CURRENCY_VALUE_IN_SECONDS)

    response = await self.__fb.sell(accountId, clientOrderId)
    if not self.__isResponseOk(response):
      return None

    if response["o"]["status"] == "Accepted":
      self.__sendManagerMessage(session.currency_sold(buyedFor, soldFor))
    else:
      self.__restart()
      self.__sendManagerMessage(session.message.log_error(description="Erro ao vender moeda",
                                                          path="user_session.__tradeLife",
                                                          body=json.dumps(response)))
  
  async def __getCurrencyValue(self):
    response = await self.__fb.getTickerHistory()
    if not self.__isResponseOk(response):
      return None

    return response["o"]
