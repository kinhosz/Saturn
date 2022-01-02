import foxbit
import json
import asyncio
from datetime import datetime, timedelta

class Foxbit(object):
  def __init__(self, websocket):
    self.__ws = websocket
    self.__lastRequestTime = None

  def __basicRequest(self, endpoint=""):
    response = {
      "m": 0, # MessageType ( 0_Request / 1_Reply / 2_Subscribe / 3_Event / 4_Unsubscribe / Error )
      "i": 0, # Sequence Number
      "n": endpoint, # Endpoint
      "o": "" # Payload
    }

    return response

  async def __wait(self):
    if self.__lastRequestTime == None:
      self.__lastRequestTime = datetime.now()
    else:
      seconds = foxbit.DELAY_FOR_REQUESTS_IN_SECONDS - (datetime.now() - self.__lastRequestTime).seconds
      await asyncio.sleep(seconds)
      self.__lastRequestTime = datetime.now()

  def __buildRequest(self, endpoint, **kwargs):
    request = self.__basicRequest(endpoint)

    if endpoint == "WebAuthenticateUser":
      request["o"] = self.__payloadForAuthenticate(**kwargs)
    
    elif endpoint == "GetInstrument":
      request["o"] = self.__payloadForGetInstrument()
    
    elif endpoint == "GetProducts":
      request["o"] = self.__payloadForGetProducts()

    elif endpoint == "GetTickerHistory":
      request["o"] = self.__payloadForGetTickerHistory()

    elif endpoint == "GetUserInfo":
      request["o"] = self.__payloadForGetUserInfo()

    elif endpoint == "GetOpenOrders":
      request["o"] = self.__payloadForGetOpenOrders(**kwargs)

    elif endpoint == "GetOrderHistory":
      request["o"] = self.__payloadForGetOrderHistory(**kwargs)

    elif endpoint == "GetAccountTrades":
      request["o"] = self.__payloadForGetAccountTrades(**kwargs)

    elif endpoint == "SendOrder":
      request["o"] = self.__payloadForSendOrder(**kwargs)

    return json.dumps(request)

  async def __sendRequest(self, request):
    await self.__wait() # wait for avoiding make excessive requests

    try:
      await self.__ws.send(request)
      str_response = await self.__ws.recv()

      response = json.loads(str_response)
      response["o"] = json.loads(response["o"])

      response["status"] = "Success" 
    except:
      response = {
        "status": "Failed",
        "description": "An error occur during send and receive request from websocket"
      }

    return response

  # payloads

  def __payloadForAuthenticate(self, username, password):
    payload = {
      "UserName": username,
      "Password": password
    }
    
    return json.dumps(payload)

  def __payloadForGetInstrument(self):
    payload = {
      "OMSId": 1,
      "InstrumentId": 1
    }

    return json.dumps(payload)

  def __payloadForGetProducts(self):
    payload = {
      "OMSId": 1
    }

    return json.dumps(payload)

  '''-----------------------------------------------------------
    The foxbit API documentation is leak, so, NOT USE a seconds in
    datetime within this request different to zero.
  ------------------------------------------------------------'''
  def __payloadForGetTickerHistory(self):
    current = datetime.now()
    current = current - timedelta(seconds=current.second)

    payload = {
      "InstrumentId": 1,
      "Interval": 60,
      "FromDate": (current - timedelta(minutes=1)).strftime('%Y-%m-%dT%H:%M:%S'),
      "ToDate": current.strftime('%Y-%m-%dT%H:%M:%S')
    }

    return json.dumps(payload)

  def __payloadForGetUserInfo(self):
    payload = {}

    return json.dumps(payload)

  def __payloadForGetOpenOrders(self, accountId):
    payload = {
      "AccountId": accountId,
      "OMSId": 1
    }

    return json.dumps(payload)

  def __payloadForGetOrderHistory(self, accountId):
    payload = {
      "AccountId": accountId,
      "OMSId": 1
    }

    return json.dumps(payload)
  
  def __payloadForGetAccountTrades(self, accountId):
    payload = {
      "AccountId": accountId,
      "OMSId": 1,
      "StartIndex": 0,
      "Count": 1
    }

    return json.dumps(payload)

  def __payloadForSendOrder(self, accountId, **kwargs):
    payload = {
      "AccountId": accountId,
      "ClientOrderId": 99,
      "Quantity": 1,
      "DisplayQuantity": 0,
      "UseDisplayQuantity": true,
      "LimitPrice": 95,
      "OrderIdOCO": 0,
      "OrderType": 2,
      "PegPriceType": 1,
      "InstrumentId": 1,
      "TrailingAmount": 1.0,
      "LimitOffset": 2.0,
      "Side": 0,
      "StopPrice": 96,
      "TimeInForce": 1,
      "OMSId": 1
    }

    return json.dumps(payload)

  # endpoints

  async def authenticate(self, username, password):
    request = self.__buildRequest(endpoint = "WebAuthenticateUser",
                                  username = username,
                                  password = password)

    return await self.__sendRequest(request)

  async def getInstrument(self):
    request = self.__buildRequest(endpoint = "GetInstrument")

    return await self.__sendRequest(request)

  async def getProducts(self):
    request = self.__buildRequest(endpoint = "GetProducts")

    return await self.__sendRequest(request)

  async def getTickerHistory(self):
    request = self.__buildRequest(endpoint = "GetTickerHistory")
    response = await self.__sendRequest(request)

    if response["status"] == "Fail":
      return response

    try:
      listPayload = response["o"]
    except:
      print(response)
    # an easy way to understand the response
    responsePayload = {
      "UTC": listPayload[-1][0],
      "High": listPayload[-1][1],
      "Low": listPayload[-1][2],
      "Open": listPayload[-1][3],
      "Close": listPayload[-1][4],
      "Volume": listPayload[-1][5],
      "Bid": listPayload[-1][6],
      "Ask": listPayload[-1][7],
      "InstrumentId": listPayload[-1][8]
    }

    response["o"] = responsePayload

    return response

  async def getUserInfo(self):
    request = self.__buildRequest(endpoint = "GetUserInfo")
    return await self.__sendRequest(request)

  async def getOpenOrders(self, accountId):
    request = self.__buildRequest(endpoint = "GetOpenOrders",
                                  accountId = accountId)

    return await self.__sendRequest(request)
  
  async def getOrderHistory(self, accountId):
    request = self.__buildRequest(endpoint = "GetOrderHistory",
                                  accountId = accountId)
    
    return await self.__sendRequest(request)

  async def getAccountTrades(self, accountId):
    request = self.__buildRequest(endpoint = "GetAccountTrades",
                                  accountId = accountId)

    return await self.__sendRequest(request)

  async def sendOrder(self):
    request = self.__buildRequest(endpoint = "SendOrder")