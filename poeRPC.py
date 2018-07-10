import asyncio
import aiohttp
import rpc
import time
import hashlib

from enum import Enum
from getdir import get_path

CLIENT_ID = '466251900157820929'

class LogEvents(Enum):
    LOGIN = 0
    LOGOUT = 1
    AREA = 2
class PoeRPC:
    def __init__(self, loop, account_name):
        self.rpc = rpc.DiscordIpcClient.for_platform(CLIENT_ID)
        self.log_path = None
        self.log_hash = None
        self.on = True
        self.loop = loop
        self.last_location = None
        self.last_latest_message = ""
        self.last_event = LogEvents.LOGOUT
        self.afk = False
        self.dnd = False
        self.afk_message = ""
        self.account_name = account_name
        self.current_rpc = {}

    async def check_poe(self):
        """Try to check if poe is running every 15sec, disable RPC if not.
        Try to handle running init again if poe launches again?"""
        while 1:
            poe = get_path()
            if not poe:
                # Disable RPC call here
                self.on = False
            else:
                self.on = True
            await asyncio.sleep(15)

    def update_rpc(self, field, value):
        self.current_rpc[field] = value

    def submit_update(self):
        self.rpc.set_activity(self.current_rpc)

    async def fetch_char(self):
        async with self.ses.get(f'https://www.pathofexile.com/character-window/get-characters?accountName={self.account_name}') as resp:
            json = await resp.json()
        for char in json:
            if 'lastActive' in char.keys():
                break
        asc = char['class']
        level = char['level']
        name = char['name']
        details = f"Level {level} {asc} {name}"
        self.update_rpc('details', details)
        self.update_rpc('large_image', asc.lower())

    async def get_area_data(self, name):
        pass

    async def handle_log_event(self, log):
        messages = reversed(log.split('\n'))
        event = None
        for ind, message in enumerate(messages):
            if message == self.last_latest_message:
                print('reached last msg')
                break
            elif "You have entered" in message:
                loc = message.split("You have entered ")[1].replace('.','')
                print("entered", loc)
                if self.last_location != loc:
                    event = LogEvents.AREA
                    self.last_location = loc
                else:
                    return
                break
            elif "Async connecting" in message:
                print('logout')
                self.last_location = None
                event = LogEvents.LOGOUT
                break
            elif "AFK mode is now" in message:
                print('afk')
                if message.split("AFK mode is now O")[1][0] == "N":
                    self.afk = True
                    self.afk_message = message.split('Autoreply "')[1][:-2]
                else:
                    self.afk = False
            elif "DND mode is now" in message:
                print('DND')
                if message.split("DND mode is now O")[1][0] == "N":
                    self.dnd = True
                    self.afk_message = message.split('Autoreply "')[1][:-2]
                else:
                    self.dnd = False
        self.last_latest_message = log.split('\n')[-1] or log.split('\n')[-2]
    async def monitor_log(self):
        """Monitor if log file has changed by calculating md5 hash,
        pass log to handler if yes, try again in 5 seconds"""
        print('monitor')
        while 1:
            if not self.on:
                break
            with open(self.log_path, encoding='utf-8') as f:
                log = f.read()
            #log = log.encode('utf-8')
            new_last = log.split('\n')[-1] or log.split('\n')[-2]
            print(new_last)
            if self.last_latest_message != new_last:
                print('log change')
                await self.handle_log_event(log)
            await asyncio.sleep(5)
    @staticmethod
    def get_poe():
        """When initializing, keep trying to find a launched poe before we can init here"""
        # while 1:
            # poe = get_path()
            # if not poe:
                # time.sleep(10)
            # else:
                # return poe
        return "I:/SteamLibrar/steamapps/common/Path of Exile"
    async def init(self):
        print('init')
        poe = self.get_poe()
        self.log_path = f"{poe}/logs/Client.txt"
        self.ses = aiohttp.ClientSession()
        #self.loop.ensure_future(check_poe())
        await asyncio.sleep(2)
        self.loop.create_task(self.monitor_log())