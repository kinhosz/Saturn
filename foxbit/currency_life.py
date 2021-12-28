import foxbit

class CurrencyLife(object):
  def __init__(self, historyLimit, valleyPercent, profit):
    self.__state = 0 # 0 - to buy, 1 - to sell
    self.__table = foxbit.Table(historyLimit, valleyPercent) # Todo> a data structure for this table
    self.__lockedPrice = None
    self.__historyLimit = historyLimit
    self.__valleyPercent = valleyPercent
    self.__profit = profit

  def reset(self):
    self.__state = 0 # 0 - to buy, 1 - to sell
    self.__table = foxbit.Table(self.__historyLimit, self.__valleyPercent) # Todo> a data structure for this table
    self.__lockedPrice = None

  def getState(self):
    return self.__state

  def addPrice(self, price):
    self.__table.add(price)

    return self.__table.isValley(price)

  def __changeState(self):
    self.__state = 1 # rollback is unpermitted

  def lockPrice(self, price):
    self.__lockedPrice = price
    self.__changeState()
  
  def checkProfit(self, price):
    profit = (price/self.__lockedPrice) - 1.0

    return profit >= self.__profit
    