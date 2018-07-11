import asyncio
import json

from poeRPC import PoeRPC

with open('config.json') as f:
    js = json.load(f)
if not js['name']:
    js['name'] = input("Please enter your path of exile account name: ")
    while 1:
        reply = input("Is your path of exile profile private or is character tab hidden? (y/n): ")
        if reply in ["y", "n"]:
            break
    if reply == "y":
        while 1:
            sessid = input("Input your POESESSID here: ")
            confirm = input("Confirm? (y/n)")
            if confirm in ["y", "n"]:
                if confirm == "n":
                    continue
                else:
                    break
        js['sessid'] = sessid
        js['private'] = True
    else:
        js['private'] = False
    with open('config.json', 'w') as f:
        json.dump(js, f)
        
loop = asyncio.ProactorEventLoop()
cookies = None
if js['private']:
    cookies = {'POESESSID': js['sessid']}
cl = PoeRPC(loop, js['name'], cookies)
#print(dir(loop))
loop.run_until_complete(cl.init())
loop.run_forever()