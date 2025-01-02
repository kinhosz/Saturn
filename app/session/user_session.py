import asyncio

from app.algorithms import Queue
from app import db, session
from app.foxbit.constants import DepositStage

class UserSession(object):
  def __init__(self, chat_id):
    self._id = False
    self._chat_id = chat_id
    self._username = None
    self._authenticated = False

    self._buffer = Queue()
    self._db_client = db.DatabaseClient()
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
      self._handleTelegramMessages(message["data"])

  @_catch_error
  def _handleTelegramMessages(self, message):
    if 'text' not in message.keys():
      return None

    self._handleSessionCommand(message)

  def _sendManagerMessage(self, msg):
    self._callbackBuffer.push({
      "from": "session",
      "data": {
        "id": self._chat_id,
        "message": msg
      }
    })

  @_catch_error
  def _handleSessionCommand(self, msg):
    if self._isCriticalState():
      self._handleCriticalState(msg)
    else:
      self._handleNormalCommand(msg)

  @_catch_error
  def _isCriticalState(self):
    return self._state != session.State.IDLE

  @_catch_error
  def _handleCriticalState(self, msg):
    if self._state == session.State.WAITING_FOR_DEPOSIT:
      self._handleDepositAmount(msg)

  @_catch_error
  def _handleNormalCommand(self, msg):
    text = msg['text']

    if text == '/start':
      self._sendManagerMessage(session.START)
    elif text == '/register':
      self._registerUser(msg)
    elif text == '/profile':
      self._getProfile()
    elif text == '/deposit':
      self._startDepositProcess()

  """ Session Operations """
  def _auth(func):
    def wrapper(cls, *args, **kwargs):
      if not cls._authenticated:
        cls._fetch()

      if cls._authenticated:
        func(cls, *args, **kwargs)
      else:
        cls._sendManagerMessage(session.UNAUTHORIZED)
    return wrapper

  @_catch_error
  def _fetch(self):
    res = self._db_client.find_equal(
      'users', 'telegram_chat_id', self._chat_id,
      ['id', 'active']
    )

    if len(res) > 0:
      self._id = res[0][0]
      self._authenticated = res[0][1]

  @_catch_error
  def _registerUser(self, msg):
    self._username = msg['from']['username'] if 'username' in msg['from'] else msg['from']['first_name']
    
    res = self._db_client.find_equal('users', 'telegram_chat_id', self._chat_id, ['id'])
    if len(res) != 0:
      self._sendManagerMessage(session.ACCOUNT_ALREADY_EXISTS)
      return None

    self._db_client.insert('users', ['telegram_chat_id', 'telegram_username', 'active'], [self._chat_id, self._username, False])
    self._sendManagerMessage(session.ACCOUNT_CREATED)

  @_catch_error
  def _getProfile(self):
    res = self._db_client.find_equal('users', 'telegram_chat_id', self._chat_id, ['telegram_username', 'active'])
    if len(res) == 0:
      self._sendManagerMessage(session.message.ACCOUNT_NOT_FOUND)
    else:
      self._sendManagerMessage(session.profile(res[0][0], res[0][1]))

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
      self._db_client.insert('deposits', ['user_id', 'amount', 'stage'], [self._id, amount, DepositStage.PENDING.value])
    except Exception as e:
      self._sendManagerMessage(session.error(str(e)))
      return None

    self._sendManagerMessage(session.DEPOSIT_CREATED)
    self._state = session.State.IDLE
