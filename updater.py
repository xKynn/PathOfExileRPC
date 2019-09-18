import atexit
import glob
import os
import sys
import win32api

from zipfile import ZipFile
from distutils.dir_util import copy_tree
from pkg_resources import parse_version

_dir = os.path.join(os.path.dirname(sys.executable), 'updates')


class Updater:
    def __init__(self, path_to_zip):
        self.zipfile = path_to_zip

    def extract(self):
        with ZipFile(self.zipfile, 'r') as zipf:
            print("Extracting...", os.path.join(_dir, zipf.filename.rsplit('.zip')[0]))
            if not os.path.isdir(_dir):
                os.mkdir(_dir)
            if not os.path.isdir(os.path.join(_dir, zipf.filename.rsplit('.zip')[0])):
                os.mkdir(os.path.join(_dir, zipf.filename.rsplit('.zip')[0]))

            zipf.extractall(os.path.join(_dir, zipf.filename.rsplit('.zip')[0]))
            print("Done.")
            return os.path.join(_dir, zipf.filename.rsplit('.zip')[0])

    @staticmethod
    def install(from_path):
        try:
            copy_tree(from_path, os.getcwd(), preserve_mode=1, preserve_times=1)
        except:
            pass

    def update(self):
        zpf = self.extract()
        current_info = win32api.GetFileVersionInfo('launcher.exe', "\\")
        current_ms = current_info['FileVersionMS']
        current_ls = current_info['FileVersionLS']
        current_version = "%d.%d.%d.%d" % (win32api.HIWORD(current_ms), win32api.LOWORD(current_ms),
                                           win32api.HIWORD(current_ls), win32api.LOWORD(current_ls))
        current_ver = parse_version(current_version)

        new_info = win32api.GetFileVersionInfo(os.path.join(zpf, 'launcher.exe'), "\\")
        new_ms = new_info['FileVersionMS']
        new_ls = new_info['FileVersionLS']
        new_version = "%d.%d.%d.%d" % (win32api.HIWORD(new_ms), win32api.LOWORD(new_ms),
                                       win32api.HIWORD(new_ls), win32api.LOWORD(new_ls))
        new_ver = parse_version(new_version)
        
        if new_ver > current_ver:
            self.install(zpf)
            print(f"Update Finished! {current_ver} -> {new_ver}")
        else:
            print(f"Update Failed! Package {new_ver} is either older or equivalent to the current installation {current_ver}")


if __name__ == "__main__":
    files = glob.glob(os.path.join(_dir, '*.zip'))
    latest_update = max(files, key=os.path.getctime)
    u = Updater(latest_update)
    u.update()
    print("Starting launcher again..")
    atexit.register(os.execl, "launcher.exe", "launcher.exe")
