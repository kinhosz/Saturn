import asyncio

from app.algorithms import Queue
from app import session
from app.foxbit import Foxbit
from app.foxbit.constants import DepositStage, MINIMUM_BTC_TRADING
from app.models import Balance, Deposit, TradingSetting, User

from typing import List

class UserSession(object):
  def __init__(self, chat_id):
    self._id = False
    self._chat_id = chat_id
    self._username = None
    self._authenticated = False
    self._foxbit = Foxbit()

    self._buffer = Queue()
    self._state = session.State.IDLE
    self._callbackBuffer = None

  def _catch_error(func):
    async def async_wrapper(cls, *args, **kwargs):
      try:
        return await func(cls, *args, **kwargs)
      except Exception as e:
        cls._sendManagerMessage(session.message.error_template(str(e), func.__name__))

    def sync_wrapper(cls, *args, **kwargs):
      try:
        return func(cls, *args, **kwargs)
      except Exception as e:
        cls._sendManagerMessage(session.message.error_template(str(e), func.__name__))

    if asyncio.iscoroutinefunction(func):
      return async_wrapper
    return sync_wrapper

  @_catch_error
  def getBuffer(self):
    return self._buffer

  @_catch_error
  async def listen(self, buffer):
    self._callbackBuffer = buffer
    DELAY_FOR_WAIT_MESSAGES_IN_SECONDS = 0.1

    while True:
      buffer_sz = self._buffer.size()

      for _ in range(buffer_sz):
        message = self._buffer.front()
        self._buffer.pop()
        await self._handleMsg(message)
      
      await asyncio.sleep(DELAY_FOR_WAIT_MESSAGES_IN_SECONDS)

  @_catch_error
  async def _handleMsg(self, message):
    if message["from"] == "telegram":
      await self._handleTelegramMessages(message["data"])

  @_catch_error
  async def _handleTelegramMessages(self, message):
    if 'text' not in message.keys():
      return None

    await self._handleSessionCommand(message)

  def _sendManagerMessage(self, msg):
    self._callbackBuffer.push({
      "from": "session",
      "data": {
        "id": self._chat_id,
        "message": msg
      }
    })

  @_catch_error
  async def _handleSessionCommand(self, msg):
    if self._isCriticalState():
      self._handleCriticalState(msg)
    else:
      await self._handleNormalCommand(msg)

  @_catch_error
  def _isCriticalState(self):
    return self._state != session.State.IDLE

  @_catch_error
  def _handleCriticalState(self, msg):
    if self._state == session.State.WAITING_FOR_DEPOSIT:
      self._handleDepositAmount(msg)

  @_catch_error
  async def _handleNormalCommand(self, msg):
    text = msg['text']

    if text == '/start':
      self._sendManagerMessage(session.START)
    elif text == '/register':
      self._registerUser(msg)
    elif text == '/profile':
      self._getProfile()
    elif text == '/deposit':
      self._startDepositProcess()
    elif text == '/trading_info':
      await self._getTradingInfo()
    elif text == '/trading_rebase':
      await self._tradingRebase()

  """ Session Operations """
  def _auth(func):
    async def async_wrapper(cls, *args, **kwargs):
      if not cls._authenticated:
        cls._fetch()

      if cls._authenticated:
        await func(cls, *args, **kwargs)
      else:
        cls._sendManagerMessage(session.UNAUTHORIZED)

    def sync_wrapper(cls, *args, **kwargs):
      if not cls._authenticated:
        cls._fetch()

      if cls._authenticated:
        func(cls, *args, **kwargs)
      else:
        cls._sendManagerMessage(session.UNAUTHORIZED)

    if asyncio.iscoroutinefunction(func):
      return async_wrapper
    return sync_wrapper

  @_catch_error
  def _fetch(self):
    user = User.find_by('telegram_chat_id', self._chat_id)

    if user:
      self._id = user.id
      self._authenticated = user.active

  @_catch_error
  def _registerUser(self, msg):
    self._username = msg['from']['username'] if 'username' in msg['from'] else msg['from']['first_name']

    user = User.find_by('telegram_chat_id', self._chat_id)
    if user:
      self._sendManagerMessage(session.ACCOUNT_ALREADY_EXISTS)
      return None

    user = User()
    user.telegram_chat_id = self._chat_id
    user.telegram_username = self._username
    user.active = False
    user.save()

    self._sendManagerMessage(session.ACCOUNT_CREATED)

  @_catch_error
  def _getProfile(self):
    user = User.find_by('telegram_chat_id', self._chat_id)
    if not user:
      self._sendManagerMessage(session.message.ACCOUNT_NOT_FOUND)
    else:
      self._sendManagerMessage(session.profile(user.telegram_username, user.active))

  @_catch_error
  @_auth
  def _startDepositProcess(self):
    self._sendManagerMessage(session.DEPOSIT_START)
    self._state = session.State.WAITING_FOR_DEPOSIT

  @_catch_error
  def _handleDepositAmount(self, msg):
    txt = msg['text']
    amount = 0.0
    try:
      amount = float(txt)
    except Exception as _:
      self._sendManagerMessage(session.INVALID_DEPOSIT_AMOUNT)
      return None

    self._createDeposit(amount)

  @_catch_error
  def _createDeposit(self, amount):
    try:
      deposit = Deposit()
      deposit.user_id = self._id
      deposit.amount = amount
      deposit.stage = DepositStage.PENDING.value
      deposit.save()
    except Exception as e:
      self._sendManagerMessage(session.error(str(e)))
      return None

    self._sendManagerMessage(session.DEPOSIT_CREATED)
    self._state = session.State.IDLE

  @_catch_error
  @_auth
  async def _getTradingInfo(self):
    user = User.find_by('telegram_chat_id', self._chat_id)
    trading = TradingSetting.find_by('user_id', user.id)
    balances: List[Balance] = Balance.where(user_id=[user.id])
    balance_in_brl = None
    balance_in_btc = None
    
    for b in balances:
      if b.base_symbol == 'BRL':
        balance_in_brl = b
      elif b.base_symbol == 'BTC':
        balance_in_btc = b       

    res = await self._foxbit.getCandlesticks(market_symbol='btcbrl', interval='1m', limit=1)
    btc_price = round(float(res[0]['close_price']), 2)
    btc_high = round(float(res[0]['highest_price']), 2)
    btc_low = round(float(res[0]['lowest_price']), 2)
    btc_balance = round(balance_in_btc.amount, 8)
    brl_balance = round(balance_in_brl.amount, 2)
    btc_cost = round(balance_in_btc.price, 2)
    brl_cost = round(balance_in_brl.price, 8)
    brl_desired_balance = round(brl_balance + btc_cost * trading.percentage_to_sell, 2)
    brl_current_balance = round(brl_balance + btc_balance * btc_price, 2)
    if brl_cost < MINIMUM_BTC_TRADING:
      price_to_buy = 'Saldo insuficiente'
    else:
      price_to_buy = round((brl_balance / brl_cost) * (trading.percentage_to_buy ** max(trading.exchange_count, 1.0)), 2)
    
    if btc_balance < MINIMUM_BTC_TRADING:
      price_to_sell = 'Saldo insuficiente'
    else:
      price_to_sell = round((btc_cost / btc_balance) * (trading.percentage_to_sell ** abs(min(trading.exchange_count, -1.0))), 2)

    self._sendManagerMessage(session.trading_info(
      btc_price, btc_high, btc_low, price_to_sell, price_to_buy, btc_balance, btc_cost,
      brl_balance, brl_cost, brl_current_balance, brl_desired_balance
    )) 

  @_catch_error
  async def _getRepresentativeBTCPrice(self):
    candles = await self._foxbit.getCandlesticks(market_symbol='btcbrl', interval='30m', limit=500)
    if len(candles) != 500:
      raise Exception("Candles size is different than expected!")

    sum_by_volume = 0.0
    all_volume = 0.0
    for candle in candles:
      sum_by_volume += ((candle['highest_price'] + candle['lowest_price']) / 2.0) * candle['base_volume']
      all_volume += candle['base_volume']
    
    if all_volume < 1e-8:
      raise Exception("Total volume can't be 0")

    return sum_by_volume / all_volume

  @_catch_error
  @_auth
  async def _tradingRebase(self):
    representative_price = await self._getRepresentativeBTCPrice()

    balances: List[Balance] = Balance.where(user_id=[self._id], base_symbol=['BRL'])
    balance = balances[0]

    btc_amount = balance.amount / representative_price
    balance.price = btc_amount
    balance.save()

    self._sendManagerMessage(session.BALANCE_REBASED)
