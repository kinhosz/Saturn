import db

class Trade(object):
    def __init__(self, id):
        self.__id = id
        self.__purchasePriceBRL = None
        self.__salePriceBRL = None
        self.__quantityBTC = None
        self.__open = None
        self.__walletID = None

