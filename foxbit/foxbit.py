import json

class Foxbit(object):
  def __init__(self, websocket):
    self.__ws = websocket

  def __basicRequest(self, endpoint=""):
    response = {
      "m": 0, # MessageType ( 0_Request / 1_Reply / 2_Subscribe / 3_Event / 4_Unsubscribe / Error )
      "i": 0, # Sequence Number
      "n": endpoint, # Endpoint
      "o": "" # Payload
    }

    return response

  def __buildRequest(self, endpoint, **kwargs):
    request = self.__basicRequest(endpoint)

    if endpoint == "WebAuthenticateUser":
      request["o"] = self.__payloadForAuthenticate(**kwargs)

    return json.dumps(request)

  async def __sendRequest(self, request):
    await self.__ws.send(request)
    str_response = await self.__ws.recv()

    response = json.loads(str_response)
    response["o"] = json.loads(response["o"])

    return response

  async def authenticate(self, username, password):
    request = self.__buildRequest(endpoint = "WebAuthenticateUser",
                                  username = username,
                                  password = password)

    return await self.__sendRequest(request)

  # payloads

  def __payloadForAuthenticate(self, username, password):
    payload = {
      "UserName": username,
      "Password": password
    }
    
    return json.dumps(payload)
