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