from BaseCleaner.BaseCleaner import BaseCleaner
import pathlib

class PrefetchCleaner(BaseCleaner):
    def __init__(self, path: pathlib.Path,dry_run: bool = False):
        self.path = path
        super().__init__(path,"Prefetch",dry_run=dry_run)