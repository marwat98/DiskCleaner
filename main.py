import pathlib
import logging
from Admin.Admin import is_admin , relaunch_as_admin
from CleanupMenager.CleanupManager import CleanupManager

INCLUDE_PREFETCH = False

def main():
    if is_admin is False:
        return relaunch_as_admin()

