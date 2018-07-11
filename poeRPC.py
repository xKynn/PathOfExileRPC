import asyncio
import aiohttp
import rpc
import time
import hashlib
import time
import json

from enum import Enum
from getdir import get_path
from pathlib import Path

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
        self.locations = {}
        with open('areas.json') as f:
            areas = json.load(f)
        self.locations.update(areas)
        self.locations['guardians'] = ['forge of the phoenix', 'maze of the minotaur', 'lair of the hydra', 'pit of the chimera']
        with open('maps.json') as f:
            self.maps = json.load(f)
        

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
    def update_subdict(self, subdict, field, value):
        if subdict not in self.current_rpc.keys():
            self.current_rpc[subdict] = {}
        self.current_rpc[subdict][field] = value
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
        details = f"{name} | Level {level} {asc} in {char['league']} league"
        self.update_rpc('details', details)
        self.update_subdict('assets', 'large_image', asc.lower())
        self.update_subdict('assets', 'large_text', details)

    @staticmethod
    def fix_names(self, name):
        return name.replace(',', '').replace("'", "").replace('ö', 'o').replace(' ', '_').lower()

    async def fetch_area_data(self, name):
        loc = None
        if 'hideout' in name.lower():
            loc = {'name': name}
            img = 'hideout'
        if not loc:
            for map in self.maps:
                if name in map['name']:
                    loc = map
                    fixed_name = self.fix_names(name)
                    p = Path.cwd().joinpath(f'assets/{fixed_name}.png')
                    if p.is_file():
                        img = fixed_name
                    elif int(map['tier']) <6:
                        img = 'white'
                    elif 6 <= int(map['tier']) <=10:
                        img = 'yellow'
                    elif int(map['tier']) > 10:
                        img = 'red'
                    elif name.lower() in self.locations['guardians']:
                        if 'Phoenix' in name:
                            img = 'phoenix'
                        elif 'Minotaur' in name:
                            img = 'minotaur'
                        elif 'Hydra' in name:
                            img = 'hydra'
                        else:
                            img = 'chimera'
                    elif name in "Vaal Temple":
                        img = 'vaal_temple'
                    break
        if not loc:
            for town in self.locations['towns']:
                if name in town['name']:
                    loc = town
                    img = 'town'
                    break
        if not loc:
            for part in self.locations['lab_rooms']:
                if part in name:
                    loc = {'name': "The Lord's Labyrinth"}
                    img = 'lab'
                    break
        if not loc:
            loc = {'name': name}
            img = 'waypoint'
        small_text = loc['name']
        timestamp = round(time.time())
        self.update_subdict('assets', 'small_text', small_text)
        self.update_subdict('assets', 'small_image', img)
        self.update_subdict('timestamps', 'start', timestamp)
        self.update_rpc('state', f'in {name}')
        if 'tier' in loc.keys():
            self.update_rpc('details', f"Tier: {loc['tier']}")
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
                if self.last_location != loc and loc != "Arena":
                    event = LogEvents.AREA
                    self.last_location = loc
                else:
                    return
                break
            elif "Async connecting" in message or "Abnormal disconnect" in message:
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
        if self.last_event == LogEvents.LOGOUT and event != LogEvents.LOGOUT:
            await self.fetch_char()
        if event == LogEvents.AREA:
            await self.fetch_area_data(loc)
        elif event == LogEvents.LOGOUT:
            self.current_rpc = {}
            self.update_subdict('assets', 'large_image', 'login_screen')
            self.update_rpc('state', 'On Character Selection')
        self.submit_update()
        self.last_event = event
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
    async def get_poe():
        """When initializing, keep trying to find a launched poe before we can init here"""
        while 1:
            poe = get_path()
            if not poe:
                await asyncio.sleep(10)
            else:
                return poe
                #return "I:/SteamLibrar/steamapps/common/Path of Exile"
    async def init(self):
        print('init')
        poe = await self.get_poe()
        self.log_path = f"{poe}/logs/Client.txt"
        self.ses = aiohttp.ClientSession()
        self.loop.create_task(self.check_poe())
        self.loop.create_task(self.monitor_log())