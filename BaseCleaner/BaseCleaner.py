import pathlib
import shutil
import logging

class BaseCleaner:
    def __init__(self, path: pathlib.Path,expected_name):
        self.deleted = 0
        self.skipped = 0
        self.path = path
        self.expected_name = str(expected_name)

    # Validation which check path and name of folder
    def validate_path(self):
        if not self.path.is_dir() or self.path.name.lower() != self.expected_name.lower():
            logging.error(f"Error: {self.path} is not a valid path")
            return False
        return True

    # Function which clean all files
    def clean(self):
        if not self.validate_path():
            return
        for path in self.path.iterdir():
           try:
            if path.is_symlink() or path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
            self.deleted += 1
           except OSError as e:
               self.skipped += 1
               logging.error(f"Error: {e}")

    # Function which is rewriting via SoftwareDistribution
    def prepare(self):
        pass
    # Function which is rewriting via SoftwareDistribution
    def finish(self):
        pass
    def run(self):
        try:
            self.prepare()
            self.clean()
        finally:
            self.finish()