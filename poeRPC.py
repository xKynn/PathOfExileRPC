import asyncio
import rpc
import time
import hashlib

from getdir import get_path

CLIENT_ID = 466251900157820929

class PoeRPC:
    def __init__(self, loop):
        self.rpc = rpc.DiscordIpcClient.for_platform(CLIENT_ID)
        self.log_path = None
        self.log_hash = None
        self.on = False
        self.loop = loop

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

    async def monitor_log(self):
        """Monitor if log file has changed by calculating md5 hash,
        pass log to handler if yes, try again in 5 seconds"""
        while 1:
            if not self.on:
                break
            with open(self.log_path, encoding='utf-8') as f:
                log = f.read()
            m = hashlib.md5()
            hx = m.update(log.encode('utf-8')).hexdigest()
            if self.log_hash and self.log_hash != hx:
                # Log update event!
                pass
            await asyncio.sleep(5)
    @staticmethod
    def get_poe():
        """When initializing, keep trying to find a launched poe before we can init here"""
        while 1:
            poe = get_path()
            if not poe:
                time.sleep(10)
            else:
                return poe

    async def init(self):
        poe = self.get_poe()
        self.log_path = f"{poe}/logs/Client.txt"