import ctypes
import subprocess
import sys

def is_admin():
    try:
        ctypes.windll.shell32.is_admin()
        return True
    except Exception:
        return False

def relaunch_as_admin():
    params = subprocess.list2cmdline(sys.argv)
    result = ctypes.windll.shell32.ShellExecuteW(
        None,"runas",sys.executable,params,None,1 )
    if result > 32:
        sys.exit(0)
    return False

