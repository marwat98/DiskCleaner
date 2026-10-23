import logging
import os
import pathlib
import time
import traceback

from Admin.Admin import is_admin, relaunch_as_admin
from CleanupManager.CleanupManager import CleanupManager
from DiskCleaner.DiskCleaner import DiskCleaner
from PrefetchCleaner.PrefetchCleaner import PrefetchCleaner
from SoftwareDistribution.SoftwareDistributionCleaner import SoftwareDistributionCleaner
from TempCleaner.TempCleaner import TempCleaner


INCLUDE_PREFETCH = False
DRY_RUN = False

LOG_FILE = pathlib.Path(__file__).resolve().parent / "cleanup.log"


def wait_until_closed():

    print("\nZakończono oczyszczanie dysku.")
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        pass


def main():
    if not is_admin():
        relaunch_as_admin()
        print("Program wymaga uprawnień administratora.")
        wait_until_closed()
        return

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logging.info(f"Rozpoczęto czyszczenie, tryb na sucho: {DRY_RUN}")

    windows_dir = pathlib.Path(os.environ["SystemRoot"])
    user_temp = pathlib.Path(os.environ["TEMP"])
    system_drive = pathlib.Path(os.environ["SystemDrive"] + "\\")

    manager = CleanupManager()
    manager.add(TempCleaner(user_temp, dry_run=DRY_RUN))
    manager.add(TempCleaner(windows_dir / "Temp", dry_run=DRY_RUN))

    if INCLUDE_PREFETCH:
        manager.add(PrefetchCleaner(windows_dir / "Prefetch", dry_run=DRY_RUN))

    if not DRY_RUN:
        manager.add(
            SoftwareDistributionCleaner(
                windows_dir / "SoftwareDistribution" / "Download"
            )
        )
        manager.add(DiskCleaner(system_drive))
    else:
        logging.info("Tryb na sucho: pomijam SoftwareDistribution i Disk Cleanup")

    print("DiskCleaner")
    print("Trwa czyszczenie, proszę czekać...\n")
    manager.run_all()

    report = manager.summary()
    logging.info("Podsumowanie:\n" + report)
    print("Czyszczenie zakończone.\n")
    print(report)
    wait_until_closed()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        error = traceback.format_exc()
        logging.error(error)
        print("Wystąpił błąd:\n")
        print(error)
        print(f"Szczegóły w pliku: {LOG_FILE}")
        wait_until_closed()