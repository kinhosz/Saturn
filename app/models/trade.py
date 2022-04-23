import db

class Trade(object):
    def __init__(self, id):
        self.__id = id
        self.__purchasePriceBRL = None
        self.__salePriceBRL = None
        self.__quantityBTC = None
        self.__open = None
        self.__walletID = None

    def purchasePriceBRL(self):
        if self.__purchasePriceBRL != None:
            return self.__purchasePriceBRL
        
        sql = "SELECT purchase_price_BRL " \
            + "FROM trades " \
            + "WHERE id = " + str(self.__id)
        
        self.__purchasePriceBRL = db.manual(sql)[0][0]

        return self.__purchasePriceBRL
    
    def salePriceBRL(self):
        if self.__salePriceBRL != None:
            return self.__salePriceBRL
        
        sql = "SELECT sale_price_BRL " \
            + "FROM trades " \
            + "WHERE id = " + str(self.__id)
        
        self.__salePriceBRL = db.manual(sql)[0][0]

        return self.__salePriceBRL
    
    def quantityBTC(self):
        if self.__quantityBTC != None:
            return self.__quantityBTC
        
        sql = "SELECT quantity_BTC " \
            + "FROM trades " \
            + "WHERE id = " + str(self.__id)
        
        self.__quantityBTC = db.manual(sql)[0][0]

        return self.__quantityBTC
    
    def open(self):
        if self.__open != None:
            return self.__open
        
        sql = "SELECT open " \
            + "FROM trades " \
            + "WHERE id = " + str(self.__id)
        
        self.__open = db.manual(sql)[0][0]

        return self.__open
    
    def walletID(self):
        if self.__walletID != None:
            return self.__walletID
        
        sql = "SELECT wallet_id " \
            + "FROM trades " \
            + "WHERE id = " + str(self.__id)
        
        self.__walletID = db.manual(sql)[0][0]

        return self.__walletID
