import logging

class CleanupManager:
    def __init__(self):
        self.cleaners = []
        self.failed_cleaners = []

    def add(self,cleaner):
        self.cleaners.append(cleaner)

    def run_all(self):
        for cleaner in self.cleaners:
            try:
                cleaner.run()
            except Exception as e:
                logging.exception(f'{type(cleaner).__name__} failed: {e}')
                self.failed_cleaners.append(type(cleaner).__name__)

    def summary(self):
        lines = []
        total_deleted = 0
        total_skipped = 0
        total_freed = 0
        for cleaner in self.cleaners:
            name = type(cleaner).__name__
            if name in self.failed_cleaners:
                lines.append(f"{name} Failed")
            else:
                lines.append(f"{name} Deleted")
                total_deleted += cleaner.deleted
                total_skipped += cleaner.skipped
                total_freed += cleaner.freed
        lines.append(f'Total Deleted: {total_deleted}')
        lines.append(f'Total Skipped: {total_skipped}')
        lines.append(f'Total Freed: {total_freed}')
        return "\n".join(lines)
