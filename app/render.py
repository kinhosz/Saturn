import asyncio
from telegram import TServer
from session import Manager

async def render():
  tServer = TServer()
  manager = Manager()

  manager.setServerBuffer(tServer.getBuffer())  

  tasks = []

  tasks.append(asyncio.create_task(tServer.listenTelegram(manager.getBuffer())))
  tasks.append(asyncio.create_task(manager.listen()))
  tasks.append(asyncio.create_task(tServer.listenBuffer()))

  await asyncio.gather(*tasks)
