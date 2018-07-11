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

### Using / Installing  
#### Method 1 (Much easier)  
1. Head to the releases tab on the top
2. Download the latest release
3. edit config.json, replace xKynn with your account name
4. Run launcher.exe
  
#### Method 2
Setting this up is actually super easy, though be warned it at the moment prints out a lot of garbage debug stuff on the console.  
1. You need to have Python 3.6 (https://www.python.org/downloads/latest) While installing this make sure you tick these 2 Options.  
    - Add python to PATH
    - py launcher
2. download/clone the repo using the green button on the top right.  
3. To get it to work for your account, edit config.json with any text editor and replace xKynn with your account name.  
4. Double click setup.bat and then run.bat
    - If setup.bat errors with access denied, right click and run it as admin
