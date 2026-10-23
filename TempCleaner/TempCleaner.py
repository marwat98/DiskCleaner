from BaseCleaner.BaseCleaner import BaseCleaner
import pathlib

class TempCleaner(BaseCleaner):
    def __init__(self,path: pathlib.Path,dry_run: bool = False):
        self.path = path
        super().__init__(path,"Temp",dry_run=dry_run)



