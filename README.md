# DiskCleaner

A Python tool for Windows that frees up disk space by cleaning temporary and cache folders and running the built-in Windows Disk Cleanup utility.

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

## Requirements

- Windows 10 / 11
- Python 3.10+
- Administrator rights (requested automatically at startup)
- `pytest` (only for running tests)

## One-time setup

Disk Cleanup needs a saved profile describing what to clean. Do this once:

1. Open a terminal **as administrator**.
2. Run `cleanmgr /sageset:64`
3. Select the categories you want to clean and confirm with **OK**.

The program later runs `cleanmgr /sagerun:64`, which uses these saved settings.

> **Careful:** the *Recycle Bin* category empties it permanently, and the *Downloads* category (if present) deletes your entire Downloads folder. Select them only if you really want to.

## Usage

Run from the project root:

```
python main.py
```

If the program is not running as administrator, it will relaunch itself and show a UAC prompt. Progress and the final summary are shown in the terminal window, which stays open until you close it. Details are written to `cleanup.log` next to `main.py`.

> Disk Cleanup can take from a few seconds to several minutes depending on the selected categories.

### Configuration

| Setting | Location | Default | Description |
|---|---|---|---|
| `DRY_RUN` | `main.py` | `False` | When `True`, only logs what would be deleted. SoftwareDistribution and Disk Cleanup are skipped. |
| `INCLUDE_PREFETCH` | `main.py` | `False` | Enables cleaning the Prefetch folder. Windows rebuilds it, but programs may start slower for a while. |
| `PROFILE` | `DiskCleaner` class | `64` | Disk Cleanup profile number used with `/sageset` and `/sagerun`. |

> Tip: run with `DRY_RUN = True` first to see what would be removed.

## Run automatically at logon

Create a scheduled task (run in a terminal **as administrator**, adjust paths to your project location):

```
schtasks /Create /TN "DiskCleaner" /TR "\"C:\path\to\DiskCleaner\.venv\Scripts\python.exe\" \"C:\path\to\DiskCleaner\main.py\"" /SC ONLOGON /RL HIGHEST /DELAY 0001:00 /F
```

- `/RL HIGHEST` runs with administrator rights, so no UAC prompt appears
- `/DELAY 0001:00` waits one minute after logon so system startup is not slowed down

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
- **Admin** – checks for administrator rights and relaunches the program with UAC.

All system paths are built from environment variables (`SystemRoot`, `TEMP`, `SystemDrive`), so the tool works regardless of which drive Windows is installed on.

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
├── main.py                       # entry point
└── pyproject.toml
```

## Running tests

From the project root:

```
pytest -v
```

Tests use temporary folders and fake cleaners — they never touch real system folders or Windows services.

## Disclaimer

This tool deletes files. Use it at your own risk and review the code before running it on your system.
