# PathOfExileRPC
Discord RPC Client for Path of exile
## WIP
### How it works  
1. Get path of exile directory if game is running.  
2. If not, poll every 30s for game running
3. Get path from getdir
4. Poll Client.txt for events, events are as follows:
    - Login
    - Logout
    - Area - Entering a new Area
5. Depending on event:
    - Login: poll character API for path of exile, fetch latest character level and ascendancy/class, update RPC
    - Logout: Update RPC as logged out
    - Area: Fetch map icon if map, update RPC
  
### TODO:
1. Decide on offline or online assets
2. Poll for logout?
3. Log parsing
    - Check how many of the last messages?
4. Poll Character API every x interval? Maybe check for if the character has levelled up since login
    - Reminder for me: https://www.pathofexile.com/character-window/get-characters?accountName=xKynn valid char api call
