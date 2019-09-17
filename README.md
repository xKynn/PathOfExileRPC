# PathOfExileRPC
Discord RPC Client for Path of exile
### Shameless Donation Link Plug
As a college student i can only work on these fun projects in my free time, i would love if you can help me out!
<a href='https://ko-fi.com/D1D6EXXV' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://az743702.vo.msecnd.net/cdn/kofi2.png?v=0' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>  
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
1. Create sysTray attachment for updates, balloon notifications, settings and accessible way to close a running process.

### Using / Installing  
#### Method 1 (Recommended)  
1. Head to the releases tab on the top / Alternatively access the latest release from [here](https://github.com/xKynn/PathOfExileRPC/releases/latest)
2. Download the latest release
3. Run launcher.exe
  
#### Method 2
Setting this up is actually super easy, though be warned it at the moment prints out a lot of garbage debug stuff on the console.  
1. You need to have Python 3.6 (https://www.python.org/downloads/latest) While installing this make sure you tick these 2 Options.  
    - Add python to PATH
    - py launcher
2. download/clone the repo using the green button on the top right.  
3. To get it to work for your account, edit config.json with any text editor and replace xKynn with your account name.  
4. Double click setup.bat and then run.bat
    - If setup.bat errors with access denied, right click and run it as admin
### Attributions
#### [qwertyquerty](https://github.com/qwertyquerty) for [pypresence](https://github.com/qwertyquerty/pypresence)
