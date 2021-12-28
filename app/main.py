import json
import foxbit
from datetime import datetime
import os

def readCredentials():
  cred = {
    "email": os.getenv('email'),
    "password": os.getenv('password')
  }

  return cred

def log_register(logger):
  f = open("logger.json", "w")
  f.write(json.dumps(logger))
  f.close()

async def main(foxbit_API):

  user = readCredentials()

  response = await foxbit_API.authenticate(username=user["email"], password=user["password"])
  if not response["o"]["Authenticated"]:
    raise Exception("Cannot be authenticate")
  else:
    print("Authenticated")

  cLife = foxbit.CurrencyLife(historyLimit = 5000,
                              valleyPercent = 0.1,
                              profit = 0.1)
  logger = {}
  order_id = 0
  
  while True:
    response = await foxbit_API.getTickerHistory()

    if response["status"] == "Failed":
      print("##############################################")
      print("Erro no envio da mensagem")
      print("##############################################")
      break

    if cLife.getState() == 0:
      ask = response["o"]["Ask"]
      print(f"Ask price: {ask}")

      if cLife.addPrice(ask):
        logger[order_id] = {
          "Buy": {
            "UTC": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            "price": ask
          }
        }
        cLife.lockPrice(ask)
        print("-----------------------------")
        print("Locked price:", ask)
        print("-----------------------------")
        log_register(logger)

    else:
      bid = response["o"]["Bid"]
      print(f"Bid price: {bid}")
      if cLife.checkProfit(bid):
        logger[order_id] = {
          "Sell":{
            "UTC": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            "price": bid
          }
        }
        order_id += 1

        print("-----------------------------")
        print("Sell:", bid)
        print("-----------------------------")
        log_register(logger)
        cLife.reset()
