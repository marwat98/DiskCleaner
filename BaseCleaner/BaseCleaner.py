import logging
import pathlib
import shutil


class BaseCleaner:
    def __init__(self, path: pathlib.Path, expected_name: str, dry_run: bool = False):
        self.deleted = 0
        self.skipped = 0
        self.freed = 0
        self.path = path
        self.expected_name = expected_name
        self.dry_run = dry_run

    def validate_path(self):
        if not self.path.is_dir() or self.path.name.lower() != self.expected_name.lower():
            logging.error(f"Invalid path: {self.path}")
            return False
        return True

    def _size(self, item: pathlib.Path):
        try:
            if item.is_symlink():
                return 0
            if item.is_file():
                return item.stat().st_size
        except OSError:
            return 0

        total = 0
        for sub in item.rglob("*"):
            try:
                if sub.is_file() and not sub.is_symlink():
                    total += sub.stat().st_size
            except OSError:
                pass
        return total

    def clean(self):
        if not self.validate_path():
            return

        for item in self.path.iterdir():
            size = self._size(item)

            if self.dry_run:
                logging.info(f"[DRY RUN] Would delete: {item}")
                self.deleted += 1
                self.freed += size
                continue

            try:
                if item.is_symlink() or item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
                self.deleted += 1
                self.freed += size
            except OSError as e:
                self.skipped += 1
                logging.warning(f"Skipped {item}: {e}")

    def prepare(self):
        pass

    def finish(self):
        pass

    def run(self):
        try:
            self.prepare()
            self.clean()
        finally:
            self.finish()