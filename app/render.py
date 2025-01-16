import asyncio
from app.telegram import TServer
from app.session import Manager
from app.foxbit import FServer

async def render():
  tServer = TServer()
  manager = Manager()
  fServer = FServer()

  manager.setServerBuffer(tServer.getBuffer())
  fServer.setTelegramBuffer(tServer.getBuffer())

  tasks = []

  tasks.append(asyncio.create_task(tServer.listenTelegram(manager.getBuffer())))
  tasks.append(asyncio.create_task(manager.listen()))
  tasks.append(asyncio.create_task(tServer.listenBuffer()))
  tasks.append(asyncio.create_task(fServer.listen()))

  await asyncio.gather(*tasks)
