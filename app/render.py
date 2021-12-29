import asyncio
from telegram import TServer
from session import Manager

async def render():
  tServer = TServer()
  manager = Manager()

  manager.setSender(tServer.getSender())

  tasks = []

  tasks.append(asyncio.create_task(tServer.listen(manager.getBuffer())))
  tasks.append(asyncio.create_task(manager.listen()))

  asyncio.gather(*tasks)
