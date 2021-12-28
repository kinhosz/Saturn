import asyncio
import app
import telegram
import os
from dotenv import load_dotenv

async def main():
  load_dotenv()
  
  tasks = []
  tasks.append(asyncio.create_task(telegram.render()))

  await asyncio.gather(*tasks)

if __name__ == "__main__":
  asyncio.run(main())