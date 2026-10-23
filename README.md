# DiskCleaner

A tool for Windows that frees up disk space by cleaning temporary and cache folders and running the built-in Windows Disk Cleanup utility. Written in Python, distributed as a standalone `.exe`.

## Features

- Cleans the user's **Temp** folder (`%TEMP%`)
- Cleans the system **Temp** folder (`C:\Windows\Temp`)
- Cleans **SoftwareDistribution\Download** (stops Windows Update services before cleaning and restarts them afterwards)
- Optionally cleans **Prefetch** (disabled by default)
- Runs **Disk Cleanup** (`cleanmgr`) with a saved profile and measures freed space
- **Dry-run mode** – preview what would be deleted without deleting anything
- Skips files that are in use instead of failing
- Continues with remaining tasks if one of them fails
- Shows a summary report in the terminal and writes a log file
- Requests administrator rights via UAC — **no passwords are stored**
- Can run automatically at logon via Windows Task Scheduler (no UAC prompt)
- Builds into a standalone `.exe` — **Python is not required** to run it

## Requirements

**To run the `.exe`:**
- Windows 10 / 11
- Administrator rights (requested automatically at startup)

**To run from source or build the `.exe`:**
- Python 3.10+
- `pytest` (for tests)
- `pyinstaller` (for building)

## One-time setup

Disk Cleanup needs a saved profile describing what to clean. Do this once:

1. Open a terminal **as administrator**.
2. Run `cleanmgr /sageset:64`
3. Select the categories you want to clean and confirm with **OK**.

The program later runs `cleanmgr /sagerun:64`, which uses these saved settings.

> **Careful:** the *Recycle Bin* category empties it permanently, and the *Downloads* category (if present) deletes your entire Downloads folder. Select them only if you really want to.

## Usage

**Standalone:** double-click `DiskCleaner.exe` and confirm the UAC prompt.

**From source** (in the project root):

```
python main.py
```

If the program is not running as administrator, it will request elevation via UAC. Progress and the final summary are shown in the terminal window, which stays open until you close it.

The log file is written to:

```
C:\ProgramData\DiskCleaner\cleanup.log
```

> Disk Cleanup can take from a few seconds to several minutes depending on the selected categories.

### Configuration

| Setting | Location | Default | Description |
|---|---|---|---|
| `DRY_RUN` | `main.py` | `False` | When `True`, only logs what would be deleted. SoftwareDistribution and Disk Cleanup are skipped. |
| `INCLUDE_PREFETCH` | `main.py` | `False` | Enables cleaning the Prefetch folder. Windows rebuilds it, but programs may start slower for a while. |
| `PROFILE` | `DiskCleaner` class | `64` | Disk Cleanup profile number used with `/sageset` and `/sagerun`. |

> Tip: run with `DRY_RUN = True` first to see what would be removed. Rebuild the `.exe` after changing any setting.

## Building the executable

In the project root, with the virtual environment active:

```
python -m pip install pyinstaller
python -m PyInstaller --onedir --console --uac-admin --name DiskCleaner --icon DiskCleaner.ico --paths . --noconfirm main.py
```

The result is in `dist\DiskCleaner\` — `DiskCleaner.exe` together with its supporting files. Keep the whole folder; the `.exe` will not run on its own without it.

- `--onedir` – folder build (fewer antivirus false positives than a single file)
- `--console` – keeps the terminal window for the summary
- `--uac-admin` – the `.exe` requests administrator rights on start
- `--icon` – application icon

## Run automatically at logon

Create a scheduled task (run in a terminal **as administrator**, adjust the path to where `DiskCleaner.exe` is located):

```
schtasks /Create /TN "DiskCleaner" /TR "\"C:\path\to\DiskCleaner\DiskCleaner.exe\"" /SC ONLOGON /RL HIGHEST /DELAY 0001:00 /F
```

- `/RL HIGHEST` runs with administrator rights, so no UAC prompt appears
- `/DELAY 0001:00` waits one minute after logon so system startup is not slowed down

To run weekly instead (e.g. Mondays at 18:00), replace `/SC ONLOGON /DELAY 0001:00` with `/SC WEEKLY /D MON /ST 18:00`.

Test it without restarting:

```
schtasks /Run /TN "DiskCleaner"
```

Remove the task:

```
schtasks /Delete /TN "DiskCleaner" /F
```

## How it works

- **BaseCleaner** – base class. Validates the target path (must be an existing folder with the expected name), deletes its contents, counts deleted / skipped items and freed space, and supports dry-run mode. Its `run()` method always executes `prepare → clean → finish`, and `finish` is guaranteed to run even if cleaning fails.
- **TempCleaner**, **PrefetchCleaner** – subclasses that only set the expected folder name.
- **SoftwareDistributionCleaner** – overrides `prepare` / `finish` to stop and restart the `wuauserv` and `bits` services.
- **DiskCleaner** – overrides `clean` to run `cleanmgr` and measure free disk space before and after.
- **CleanupManager** – runs all registered cleaners, isolates failures and builds the summary report.
- **Admin** – checks for administrator rights and relaunches the program with UAC (works both from source and as `.exe`).

All system paths are built from environment variables (`SystemRoot`, `TEMP`, `SystemDrive`, `ProgramData`), so the tool works regardless of which drive Windows is installed on.

### Safety

- Every cleaner validates its folder name before deleting anything — if a path is wrong or empty, nothing is removed.
- Only the **contents** of target folders are deleted, never the folders themselves.
- Symbolic links are removed as links; their targets are never followed.
- Windows services are always restarted, even after an error.

## Project structure

```
DiskCleaner/
├── Admin/                        # admin check and UAC relaunch
├── BaseCleaner/                  # base cleaner class
├── TempCleaner/
├── PrefetchCleaner/
├── SoftwareDistribution/         # SoftwareDistributionCleaner
├── DiskCleaner/
├── CleanupManager/
├── Test/                         # pytest tests
├── DiskCleaner.ico               # application icon
├── DiskCleaner.spec              # PyInstaller build settings
├── main.py                       # entry point
└── pyproject.toml
```

Each package folder contains an empty `__init__.py`. The `build/` and `dist/` folders are created by PyInstaller and are not committed.

## Running tests

From the project root:

```
pytest -v
```

Tests use temporary folders and fake cleaners — they never touch real system folders or Windows services.

## Disclaimer

This tool deletes files. Use it at your own risk and review the code before running it on your system.
