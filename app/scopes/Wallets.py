import db
from models import Wallet

def need_relocation(current_price):
    sql = "SELECT id " \
        + "FROM wallets " \
        + "WHERE floor > " + str(current_price)
    
    wallet_ids = db.manual(sql)
    wallets = []

    for id in wallet_ids:
        wallet = Wallet(id[0])
        wallets.append(wallet)
    
    return wallets

