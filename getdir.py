import sys
import os.path
import ctypes
import ctypes.wintypes
import string


from ctypes import windll
from pathlib import Path

psapi = ctypes.WinDLL('psapi.dll')
EnumProcesses = psapi.EnumProcesses
EnumProcesses.restype = ctypes.wintypes.BOOL
GetProcessImageFileName = psapi.GetProcessImageFileNameA
GetProcessImageFileName.restype = ctypes.wintypes.DWORD
kernel32 = ctypes.WinDLL('kernel32.dll')
OpenProcess = kernel32.OpenProcess
OpenProcess.restype = ctypes.wintypes.HANDLE
CloseHandle = kernel32.CloseHandle

drives = []
bitmask = kernel32.GetLogicalDrives()
for letter in string.ascii_uppercase:
    if bitmask & 1:
        drives.append(letter)
    bitmask >>= 1

def get_path():
    arch = 32
    found = False
    while True:
        ProcessIds = (ctypes.wintypes.DWORD*arch)()
        cb = ctypes.sizeof(ProcessIds)
        BytesReturned = ctypes.wintypes.DWORD()
        if EnumProcesses(ctypes.byref(ProcessIds), cb, ctypes.byref(BytesReturned)):
            if BytesReturned.value<cb:
                break
            else:
                arch *= 2
        else:
            sys.exit("Call to EnumProcesses failed")

    for index in range(int(BytesReturned.value / ctypes.sizeof(ctypes.wintypes.DWORD))):
        ProcessId = ProcessIds[index]
        hProcess = OpenProcess(0x0400, False, ProcessId)
        if hProcess:
            ImageFileName = (ctypes.c_char*260)()
            if GetProcessImageFileName(hProcess, ImageFileName, 260)>0:
                filename = os.path.basename(ImageFileName.value)
                if 'PathOfExile' in filename.decode('utf-8'):
                    pt = ImageFileName.value.decode('utf-8').split('\\')
                    path = '/'.join(pt[3:])
                    found = True
                    CloseHandle(hProcess)
                    break
            CloseHandle(hProcess)

    if found:
        for drive in drives:
            p = Path(f"{drive}:/{path}")
            try:
                if p.is_file():
                    break
            except:
                continue
        return p.parent.as_posix()
    else:
        return False