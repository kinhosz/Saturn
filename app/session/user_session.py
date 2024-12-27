import asyncio

from app.algorithms import Queue
from app import db, session

class UserSession(object):
  def __init__(self, chat_id):
    self._id = chat_id
    self._username = None

    self._buffer = Queue()
    self._db_client = db.DatabaseClient()
    self._state = session.State.START
    self._callbackBuffer = None

  def getBuffer(self):
    return self._buffer

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

  async def _handleMsg(self, message):
    if message["from"] == "telegram":
      await self._handleTelegramMessages(message["data"])
    elif message["from"] == "manager":
      await self._handleManagerMessages(message["data"])

  async def _handleTelegramMessages(self, message):
    if 'text' not in message.keys():
      return None

    await self._handleSessionCommand(message)

  def _sendManagerMessage(self, msg):
    self._callbackBuffer.push({
      "from": "session",
      "data": {
        "id": self._id,
        "message": msg
      }
    })

  async def _handleSessionCommand(self, msg):
    text = msg['text']
    if text == '/start':
      self._sendManagerMessage(session.START)
    elif text == '/register':
      self._registerUser(msg)
    elif text == '/profile':
      self._getProfile()

  """ Session Operations """
  def _registerUser(self, msg):
    self._username = msg['from']['username'] if 'username' in msg['from'] else msg['from']['first_name']
    
    res = self._db_client.find_equal('users', 'telegram_chat_id', self._id, ['id'])
    if len(res) != 0:
      self._sendManagerMessage(session.ACCOUNT_ALREADY_EXISTS)
      return None

    self._db_client.insert('users', ['telegram_chat_id', 'telegram_username', 'active'], [self._id, self._username, False])
    self._sendManagerMessage(session.ACCOUNT_CREATED)

  def _getProfile(self):
    res = self._db_client.find_equal('users', 'telegram_chat_id', self._id, ['telegram_username', 'active'])
    print(res)
    self._sendManagerMessage(session.profile(res[0][0], res[0][1]))
