from cx_Freeze import setup, Executable

setup(
    name="PathOfExileRPC",
    version="",
    description='',
    executables=[Executable("launcher.py")],
    options={
        'build_exe': {
            'packages': ['aiohttp', 'idna', 'asyncio'],
            'include_files': ['pypresence/']
        },
    }
)
