import asyncio
from poeRPC import PoeRPC
loop = asyncio.get_event_loop()
cl = PoeRPC(loop, 'xKynn')
#print(dir(loop))
loop.run_until_complete(cl.init())
loop.run_forever()