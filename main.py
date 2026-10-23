import logging
import os
import pathlib

from Admin.Admin import is_admin, relaunch_as_admin
from CleanupManager.CleanupManager import CleanupManager
from DiskCleaner.DiskCleaner import DiskCleaner
from PrefetchCleaner.PrefetchCleaner import PrefetchCleaner
from SoftwareDistribution.SoftwareDistributionCleaner import SoftwareDistributionCleaner
from TempCleaner.TempCleaner import TempCleaner


INCLUDE_PREFETCH = False
DRY_RUN = True


def main():
    if not is_admin():
        relaunch_as_admin()
        print("Program wymaga uprawnień administratora.")
        input("Naciśnij Enter, aby zakończyć...")
        return

    logging.basicConfig(
        filename="cleanup.log",
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

    manager.run_all()
    print(manager.summary())
    input("Naciśnij Enter, aby zakończyć...")


if __name__ == "__main__":
    main()