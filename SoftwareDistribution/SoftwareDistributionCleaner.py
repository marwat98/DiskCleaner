import pathlib
import subprocess
import logging
from BaseCleaner.BaseCleaner import BaseCleaner

class SoftwareDistributionCleaner(BaseCleaner):
    SERVICES = ["wuauserv","bits"]

    def __init__(self, path: pathlib.Path):
        super().__init__(path,"Download")

    def _service(self,action,name):
        result = subprocess.run(["net", action,name], capture_output = True,text = True)
        if result.returncode == 0:
            logging.info(result.stdout)
        else:
            logging.warning(result.stderr)

    def prepare(self):
        for service in self.SERVICES:
            self._service("stop",service)

    def finish(self):
        for service in reversed(self.SERVICES):
            self._service("start",service)
