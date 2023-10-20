import websockets
import asyncio

async def hello(websocket):
    name = await websocket.recv()
    print(f"server received: {name}")
    greeting = f'Hello {name}'
    
    await websocket.send(greeting)
    print(f'Server sent: {greeting}')
    
async def main():
    async with websockets.serve(hello,"localhost",8765):
        await asyncio.Future()
        
if __name__ == "__main__":
    asyncio.run(main=main())
    