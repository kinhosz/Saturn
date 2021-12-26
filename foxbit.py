import websockets
import json
import asyncio

class Foxbit():
  def __init__(self):
    self.__uri = 'wss://api.foxbit.com.br/'
    self.__ws = None
    
    self.__webscocketConnect()

  def __webscocketConnect(self):
    self.__ws = yield from websockets.connect(self.__uri)
    print(self.__ws)

  def send_test(self):
    print("oi")
    messageFrame = {
      "m": 0, #MessageType ( 0_Request / 1_Reply / 2_Subscribe / 3_Event / 4_Unsubscribe / Error )
      "i": 0, #Sequence Number
      "n": "", #Endpoint
      "o": "" #Payload
    }
    print("oi")
    messageFrame["n"] = "WebAuthenticateUser"
    print("oi")
    payload = {
        "UserName": "scruz.josecarlos@gmail.com",
        "Password": "password"
    }
    print("oi")
    messageFrame["o"] = json.dumps(payload)
    self.__ws.send(json.dumps(messageFrame))
    message = self.__ws.recv()
    print("oi")
    data = json.loads(message)

    payloadr = json.loads(data["o"])
    
    if payloadr["Authenticated"] == True:
      print("Authenticated")
    else:
      print("Not authenticated")

def unit_test():
  foxbit = Foxbit()
  foxbit.send_test()
  #print(x)

if __name__ == "__main__":
  unit_test()