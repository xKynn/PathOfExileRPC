# PathOfExileRPC
Discord RPC Client for Path of exile
### How it works  
1. Get path of exile directory if game is running. (to keep this dependency free it uses a mix of ctypes, kernel32 and psapi to achieve this) 
2. If not, poll every 30s for game running
3. Get path from getdir
4. Poll Client.txt for events, events are as follows:
    - Login
    - Logout/Char selection
    - Area - Entering a new Area
5. Depending on event:
    - Login: query character API for path of exile, fetch latest character level and ascendancy/class, update RPC
    - Logout: Update RPC as logged out
    - Area: Fetch map icon if map, update RPC
  
### TODO:
1. Do something when poe exits
2. Poll Character API every x interval? Maybe check for if the character has levelled up since login
    - Reminder for me: https://www.pathofexile.com/character-window/get-characters?accountName=xKynn valid char api call
3. Experience % to next level
4. Turn into service or something for startup
