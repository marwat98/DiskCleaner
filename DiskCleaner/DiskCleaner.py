import logging
import pathlib
import subprocess
import shutil

from BaseCleaner.BaseCleaner import BaseCleaner

class DiskCleaner(BaseCleaner):
    PROFILE = 64
    def __init__(self,path: pathlib.Path):
        super().__init__(path,"")
        self.freed = 0

    # Function which automatically run cleanmgr inside program
    def _run_cleanmgr(self):
        result = subprocess.run(["cleanmgr",f'/sagerun:{self.PROFILE}'])
        if result.returncode == 0:
            logging.info(f"Cleaned {self.path}")
        else:
            logging.warning(f"Cleaned {self.path}")

    # Function which run clean disk
    def clean(self):
      before = shutil.disk_usage(self.path).free
      self._run_cleanmgr()
      after = shutil.disk_usage(self.path).free
      self.freed = max(after - before,0)
      logging.info(f"Cleaned {self.path}")
