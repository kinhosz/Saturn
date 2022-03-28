import asyncio
from telegram import TServer
from session import Manager
from foxbit import FServer

async def render():
  tServer = TServer()
  manager = Manager()
  fServer = FServer(manager.getBuffer())

  manager.setServerBuffer(tServer.getBuffer())

  tasks = []

  tasks.append(asyncio.create_task(tServer.listenTelegram(manager.getBuffer())))
  tasks.append(asyncio.create_task(manager.listen()))
  tasks.append(asyncio.create_task(tServer.listenBuffer()))
  tasks.append(asyncio.create_task(fServer.listen()))

  await asyncio.gather(*tasks)
