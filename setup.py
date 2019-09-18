from cx_Freeze import setup, Executable

setup(
    name="PathOfExileRPC",
    version="1.6",
    description='',
    executables=[Executable("launcher.py"), Executable("updater.py")],
    options={
        'build_exe': {
            'packages': ['aiohttp', 'idna', 'asyncio', 'win32com', 'win32api', 'progressbar'],
            'include_files': ['pypresence/', 'areas.json', 'available_icons.json', 'experience.json', 'maps.json']
        },
    }
)