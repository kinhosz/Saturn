import asyncio

async def receiver(tbot, buffer):
  DELAY_FOR_RECEIVE_MESSAGES_IN_SECONDS = 1

  current_id = 0
  response = tbot.getUpdates()

  if len(response) > 0:
    current_id = response[-1]['update_id'] + 1

  while True:
    response = tbot.getUpdates(offset = current_id)
    for m in response:
      current_id = m['update_id'] + 1
      buffer.push(m)
    
    await asyncio.sleep(DELAY_FOR_RECEIVE_MESSAGES_IN_SECONDS)
