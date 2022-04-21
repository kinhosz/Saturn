import db
from models import Trade

class Wallet(object):
    def __init__(self, id):
        self.__id = id
        self.__profitRate = None
        self.__totalAmountBRL = None
        self.__ceil = None
        self.__floor = None
        self.__trades = None
    
    def profitRate(self):
        if self.__profitRate != None:
            return self.__profitRate
        
        sql = "SELECT profit_rate" \
            + "FROM wallets" \
            + "WHERE id = " + str(self.__id)

        self.__profitRate = db.manual(sql)[0][0]

        return self.__profitRate
    
    def totalAmountBRL(self):
        if self.__totalAmountBRL != None:
            return self.__totalAmountBRL
        
        sql = "SELECT total_amount_BRL" \
            + "FROM wallets" \
            + "WHERE id = " + str(self.__id)

        self.__totalAmountBRL = db.manual(sql)[0][0]

        return self.__totalAmountBRL
    
    def ceil(self):
        if self.__ceil != None:
            return self.__ceil
        
        sql = "SELECT ceil" \
            + "FROM wallets" \
            + "WHERE id = " + str(self.__id)

        self.__ceil = db.manual(sql)[0][0]

        return self.__ceil
    
    def floor(self):
        if self.__floor != None:
            return self.__floor
        
        sql = "SELECT floor" \
            + "FROM wallets" \
            + "WHERE id = " + str(self.__id)

        self.__floor = db.manual(sql)[0][0]

        return self.__floor

    def trades(self):
        if self.__trades != None:
            return self.__trades
        
        sql = "SELECT id" \
            + "FROM trades" \
            + "WHERE id = " + str(self.__id)
        
        trade_ids = db.manual(sql)

        trades = []
        for t in trade_ids:
            id = t[0]
            trade = Trade(id)
            trades.append(trade)
        
        self.__trades = trades

        return self.__trades


        

    
