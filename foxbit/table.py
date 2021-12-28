from algorithms import Queue
from algorithms import Treap

class Table(object):
  def __init__(self, historyLimit, valley):
    self.__historyLimit = historyLimit
    self.__valley = valley
    self.__queue = Queue()
    self.__treap = Treap()

  def add(self, price):
    self.__treap.add(price)
    self.__queue.push(price)

    if self.__queue.size() > self.__historyLimit:
      rem_price = self.__queue.front()
      self.__queue.pop()
      self.__treap.remove(rem_price)

  def isValley(self, price):
    if self.__queue.size() != self.__historyLimit:
      return False

    rank = self.__treap.prefix(price)

    return rank <= self.__historyLimit * self.__valley

  