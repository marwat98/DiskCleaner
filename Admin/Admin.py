import ctypes
import os
import subprocess
import sys

ELEVATED_FLAG = "--elevated"


def is_admin():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def is_frozen():
    return getattr(sys, "frozen", False)


def relaunch_as_admin():
    if ELEVATED_FLAG in sys.argv:
        return False

    if is_frozen():
        args = [*sys.argv[1:], ELEVATED_FLAG]
        working_dir = os.path.dirname(sys.executable)
    else:
        script = os.path.abspath(sys.argv[0])
        args = [script, *sys.argv[1:], ELEVATED_FLAG]
        working_dir = os.path.dirname(script)

    params = subprocess.list2cmdline(args)
    result = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, params, working_dir, 1
    )
    if result > 32:
        sys.exit(0)
    return False