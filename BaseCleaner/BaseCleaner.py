import pathlib
import shutil
import logging

class BaseCleaner:
    def __init__(self, path: pathlib.Path):
        self.path = path
    def validate_path(self):
        if not self.path.is_dir():
            logging.error("Path is not a directory")
            return False
        return True

    def clean(self):












