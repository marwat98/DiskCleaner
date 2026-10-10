from BaseCleaner.BaseCleaner import BaseCleaner
import pathlib

class PrefetchCleaner(BaseCleaner):
    def __init__(self, path: pathlib.Path):
        self.path = path
        super().__init__(path,"Prefetch")