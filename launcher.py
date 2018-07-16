import asyncio
import json
import getpass

from poeRPC import PoeRPC
from shutil import copy as cp
from getdir import drives
from pathlib import Path


try:
    with open('config.json') as f:
        js = json.load(f)
except:
    js = {"name": "", "private": False, "sessid": ""}
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
    if (Path().cwd() / "launcher.exe").is_file():
        while 1:
            rep = input("Would you like to setup PathOfExileRPC to start on startup? It will start in the background without a window. (y/n)")
            if rep in ["y", "n"]:
                break
        if rep == "y":
            user = getpass.getuser()
            with open('launcher.vbs', 'w') as f:
                f.write('Set oShell = CreateObject ("Wscript.Shell")\n'
                        'Dim strArgs\n'
                        f'strArgs = "{Path().cwd()}\launcher.exe"\n'
                        'oShell.Run strArgs, 0, false')
            with open('poestartup.bat', 'w') as f:
                f.write(f"{Path().cwd().as_posix()}/launcher.vbs\nexit")
            found = False
            for drive in drives:
                p = Path(f"{drive}:/Users/{user}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup")
                if p.is_dir():
                    found = True
                    break
            if not found:
                print("The startup folder could not be located, you can set this up manually by:\n"
                      "1. Copy the newly created poestartup.bat file in this directory\n"
                      "2. Hold down the windows key and press R, in this window type in shell:startup\n"
                      "3. In the opened folder paste the file you copied earlier")
            else:
                cp('poestartup.bat', f"{p.as_posix()}/poestartup.bat")
                print("Done! PathOfExileRPC will now startup when you log into windows.")
    print("Setup is done and your settings will be saved, to go through setup again just delete the file called config.json")
    with open('config.json', 'w') as f:
        json.dump(js, f)
        
loop = asyncio.ProactorEventLoop()
cookies = None
if js['private']:
    cookies = {'POESESSID': js['sessid']}
cl = PoeRPC(loop, js['name'], cookies)
loop.run_until_complete(cl.init())
loop.run_forever()