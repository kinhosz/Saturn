class UserSession(object):
  def __init__(self, tbot, chat_id):
    self.__tbot = tbot
    self.__chatId = chat_id

  def handleMsg(self, message):
    if 'text' not in message.keys():
      return None

    print("-------------------------------------")
    print("received:", message['text'])