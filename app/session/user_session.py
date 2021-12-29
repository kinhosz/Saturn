from algorithms import Queue

class UserSession(object):
  def __init__(self, chat_id):
    self.__id = chat_id
    self.__callback = None
    self.__buffer = Queue()

  def setCallback(self, callback):
    self.__callback = callback

  def getBuffer(self):
    return self.__buffer

  async def listen(self):
    pass