import foxbit
import json
import asyncio
import websockets
from datetime import datetime, timedelta

class Foxbit(object):
  def __init__(self):
    self.__lastRequestTime = None
    # TODO: improve store credentials
    self.__username = None
    self.__password = None

  def __createErrorResponse(self, description, path, body):
    response = {
      "status": "Failed",
      "description": description,
      "path": path,
      "body": body
    }

    return response

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

  async def __websocketSend(self, request, websocket):
    errorMsg = "except: "
    error = False

    response = {
      "status": "Success"
    }

    await self.__wait()

    try:
      await websocket.send(request)
    except TypeError:
      errorMsg = errorMsg + "TypeError"
      error = True

    except websockets.exceptions.ConnectionClosedOK:
      errorMsg = errorMsg + "ConnectionClosedOK"
      error = True

    except websockets.exceptions.ConnectionClosedError:
      errorMsg = errorMsg + "ConnectionClosedError"
      error = True
      
    except websockets.exceptions.InvalidMessage:
      errorMsg = errorMsg + "InvalidMessage"
      error = True
    
    except websockets.exceptions.PayloadTooBig:
      errorMsg = errorMsg + "PayloadTooBig"
      error = True
    
    except RuntimeError:
      errorMsg = errorMsg + "RuntimeError"
      error = True

    except:
      errorMsg = errorMsg + "undefined"
      error = True
    
    if error:
      print("erro ao enviar request")
      description = "An error occur during send request to websocket. " + errorMsg
      response = self.__createErrorResponse(description=description,
                                            path="foxbit.__sendRequest",
                                            body=request)
    return response

  async def __websocketRecv(self, websocket):
    response = {}
    default_response = ""

    try:
      str_response = await websocket.recv()
    except  websockets.exceptions.ConnectionClosedOK:
      print("erro ao receber response. ok")
      response = self.__createErrorResponse(description="An error occur during receive response from websocket [closed ok]",
                                            path="foxbit.__sendRequest",
                                            body=default_response)
      return response
    
    except websockets.exceptions.ConnectionClosedError:
      print("erro ao receber response. error")
      response = self.__createErrorResponse(description="An error occur during receive response from websocket [closed error]",
                                            path="foxbit.__sendRequest",
                                            body=default_response)
      return response
    
    except websockets.exceptions.RuntimeError:
      print("erro ao receber response. rte")
      response = self.__createErrorResponse(description="An error occur during receive response from websocket [rte]",
                                            path="foxbit.__sendRequest",
                                            body=default_response)
      return response
    
    except:
      print("erro ao receber response. udf")
      response = self.__createErrorResponse(description="An error occur during receive response from websocket [udf]",
                                            path="foxbit.__sendRequest",
                                            body=default_response)
      return response 

    try:
      response = json.loads(str_response)
      response["o"] = json.loads(response["o"])
      response["status"] = "Success"
    except:
      print("erro ao manipular response")
      response = self.__createErrorResponse(description="An error occur during manipulate response from websocket",
                                            path="foxbit.__sendRequest",
                                            body=str_response)
    return response

  async def __sendRequest(self, request, authentication=False):
    response = {}

    async with websockets.connect(foxbit.URI) as websocket:
      if authentication:
        auth_request = self.__buildRequest(endpoint = "WebAuthenticateUser",
                                           username = self.__username,
                                           password = self.__password)
        response = await self.__websocketSend(auth_request, websocket)
        if response["status"] == "Failed":
          return response
        
        response = await self.__websocketRecv(websocket)
        if response["status"] == "Failed":
          return response

      response = await self.__websocketSend(request, websocket)
      if response["status"] == "Failed":
        return response
      
      await websocket.close()
      response = await self.__websocketRecv(websocket)
      if response["status"] == "Failed":
        return response

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

  def __payloadForSendOrder(self, accountId, clientOrderId, side):
    # reference: https://alphapoint.github.io/slate/#sendorder
    # reference: https://www.flowbtc.com.br/api.html
    BASE_TEST_FOR_BUY = 0.00005

    if side == 0:
      quantity = BASE_TEST_FOR_BUY
    else:
      quantity = BASE_TEST_FOR_BUY - BASE_TEST_FOR_BUY * foxbit.TAX_FOR_MARKET_ORDER

    payload = {
      "AccountId": accountId,                              # ok
      "ClientOrderId": clientOrderId,                      # ok
      "Quantity": quantity,                                 # ok
      "DisplayQuantity": 0,                                # ok
      "OrderIdOCO": 0,                                     # ok (poderia omitir)
      "OrderType": 1,                                      # ok
      "InstrumentId": 1,                                   # ok (btc)
      "Side": side,                                        # ok
      "TimeInForce": 1,                                    # ok
      "OMSId": 1                                           # ok
    }

    return json.dumps(payload)

  # endpoints

  async def authenticate(self, username, password):
    self.__username = username
    self.__password = password
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

    if response["status"] == "Failed":
      return response

    try:
      listPayload = response["o"][-1]
    except:
      errorResponse = self.__createErrorResponse(description="The response didnt have the list payload",
                                                 path="foxbit.getTickerHistory",
                                                 body=json.dumps(response))
      return errorResponse

    # an easy way to understand the response
    responsePayload = {
      "UTC": listPayload[0],
      "High": listPayload[1],
      "Low": listPayload[2],
      "Open": listPayload[3],
      "Close": listPayload[4],
      "Volume": listPayload[5],
      "Bid": listPayload[6],
      "Ask": listPayload[7],
      "InstrumentId": listPayload[8]
    }

    response["o"] = responsePayload

    return response

  async def getUserInfo(self):
    request = self.__buildRequest(endpoint = "GetUserInfo")
    return await self.__sendRequest(request, authentication=True)

  async def getOpenOrders(self, accountId):
    request = self.__buildRequest(endpoint = "GetOpenOrders",
                                  accountId = accountId)

    return await self.__sendRequest(request, authentication=True)
  
  async def getOrderHistory(self, accountId):
    request = self.__buildRequest(endpoint = "GetOrderHistory",
                                  accountId = accountId)
    
    return await self.__sendRequest(request, authentication=True)

  async def getAccountTrades(self, accountId):
    request = self.__buildRequest(endpoint = "GetAccountTrades",
                                  accountId = accountId)

    return await self.__sendRequest(request, authentication=True)

  async def __sendOrder(self, accountId, clientOrderId, side):
    request = self.__buildRequest(endpoint = "SendOrder",
                                  accountId = accountId,
                                  clientOrderId = clientOrderId,
                                  side = side)

    return await self.__sendRequest(request, authentication=True)

  async def buy(self, accountId, clientOrderId):
    return await self.__sendOrder(accountId, clientOrderId, side=0)

  async def sell(self, accountId, clientOrderId):
    return await self.__sendOrder(accountId, clientOrderId, side=1)

  # utils
  def __createResponseForUtils(self, data):
    response = {
      "status": "Sucess",
      "data": data
    }

    return response

  async def getAccountId(self):
    response = await self.getUserInfo()

    if response["status"] == "Failed":
      return response

    return self.__createResponseForUtils(response["o"]["AccountId"])

  async def getClientOrderId(self, accountId):
    response = await self.getOrderHistory(accountId)

    if response["status"] == "Failed":
      return response

    if len(response["o"]) == 0:
      return self.__createErrorResponse(description="The client didnt have any Order",
                                        path="foxbit.getClientOrderId",
                                        body= json.dumps(response))

    return self.__createResponseForUtils(response["o"][0]["ClientOrderId"])