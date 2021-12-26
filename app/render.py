import foxbit
import websockets
import app

async def render():
  async with websockets.connect(foxbit.URI) as websocket:
    fb = foxbit.Foxbit(websocket)
    await app.main(fb)