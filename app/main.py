import json

def readCredentials():

  f = open('tokens.json', 'r')
  cred = json.loads(f.read())
  f.close()

  return cred

async def main(foxbit):

  user = readCredentials()

  response = await foxbit.authenticate(username=user["email"], password=user["password"])
  print(response)