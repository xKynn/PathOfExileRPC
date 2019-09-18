import asyncio
import atexit
import json
import os
import logging
import sys
import time
if hasattr(sys, "frozen"):
    import win32api

from poeRPC import PoeRPC
from pkg_resources import parse_version
from progressbar import ProgressBar, Percentage, RotatingMarker, ETA, FileTransferSpeed, Bar
from shutil import copy as cp
from getdir import drives
from pathlib import Path
from urllib import request
from win32com.shell import shell, shellcon

logging.basicConfig(level=logging.INFO)


class Launcher:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        if hasattr(sys, "frozen"):
            resp = request.urlopen("https://api.github.com/repos/xKynn/PathOfExileRPC/releases/latest")
            data = json.load(resp)
            info = win32api.GetFileVersionInfo('launcher.exe', "\\")
            ms = info['FileVersionMS']
            ls = info['FileVersionLS']
            version = "%d.%d.%d.%d" % (win32api.HIWORD(ms), win32api.LOWORD(ms),
                                           win32api.HIWORD(ls), win32api.LOWORD(ls))
            latest_ver = parse_version(data['tag_name'])
            current_ver = parse_version(version)
            download_url = data["assets"][0]["browser_download_url"]
            if latest_ver > current_ver:
                print("Found a newer release, would you like to update? (y/n)")
                reply = input()
                if reply.startswith("n"):
                    sys.exit()
                print("Starting Update Process")
                if not os.path.isdir(os.path.join(os.path.dirname(sys.executable), 'updates')):
                    os.mkdir(os.path.join(os.path.dirname(sys.executable), 'updates'))

                widgets = [f'{data["assets"][0]["name"]}: ', Percentage(), ' ', Bar(marker=RotatingMarker()), ' ', ETA(), ' ',
                           FileTransferSpeed()]
                pbar = ProgressBar(widgets=widgets)

                def dl_progress(count, blockSize, totalSize):
                    if pbar.maxval is None:
                        pbar.maxval = totalSize
                        pbar.start()

                    pbar.update(min(count * blockSize, totalSize))

                request.urlretrieve(download_url, os.path.join(os.path.dirname(sys.executable),
                                                               'updates', data["assets"][0]["name"]),
                                    reporthook=dl_progress)
                atexit.register(os.execl, "updater.exe", "updater.exe")
                sys.exit()
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
                    rep = input(
                        "Would you like to setup PathOfExileRPC to start on startup? "
                        "It will start in the background without a window. (y/n)")
                    if rep in ["y", "n"]:
                        break
                if rep == "y":
                    user = os.getlogin()
                    with open('launcher.vbs', 'w') as f:
                        f.write('Set oShell = CreateObject ("Wscript.Shell")\n'
                                'Dim strArgs\n'
                                f'strArgs = "{Path().cwd()}\launcher.exe"\n'
                                'oShell.Run strArgs, 0, false')
                    with open('poestartup.bat', 'w') as f:
                        f.write(f"{Path().cwd().as_posix()}/launcher.vbs\nexit")
                    found = False
                    p = Path(shell.SHGetFolderPath(0, shellcon.CSIDL_STARTUP, 0, 0))
                    print(p)
                    if p.is_dir():
                        found = True
                    if not found:
                        print("The startup folder could not be located, you can set this up manually by:\n"
                              "1. Copy the newly created poestartup.bat file in this directory\n"
                              "2. Hold down the windows key and press R, in this window type in shell:startup\n"
                              "3. In the opened folder paste the file you copied earlier")
                    else:
                        cp('poestartup.bat', f"{p.as_posix()}/poestartup.bat")
                        print("Done! PathOfExileRPC will now startup when you log into windows.")
            print("Setup is done and your settings will be saved, to go through "
                  "setup again just delete the file called config.json")
            with open('config.json', 'w') as f:
                json.dump(js, f)

        self.loop = asyncio.ProactorEventLoop()
        cookies = None
        if js['private']:
            cookies = {'POESESSID': js['sessid']}

        self.cl = PoeRPC(self.loop, js['name'], cookies, self.logger)

    def run(self):
        try:
            self.loop.create_task(self.cl.init())
            self.loop.run_forever()
        except KeyboardInterrupt:
            self.logger.info("Process Interrupted.")
        finally:
            self.quit()

    def quit(self):
        self.cl.do_quit()
        if hasattr(self.loop, "shutdown_asyncgens"):
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
        self.loop.close()
        self.logger.info("PathOfExileRPC successfully shutdown.")


if __name__ == "__main__":
    launcher = Launcher()
    launcher.run()
