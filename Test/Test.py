import pathlib

import pytest
from pip._internal.network import download

from Prefetch.PrefetchCleaner import PrefetchCleaner
from Temp.TempCleaner import TempCleaner
from BaseCleaner.BaseCleaner import BaseCleaner
from SoftwareDistribution.SoftwareDistributionCleaner import SoftwareDistributionCleaner

class FakeCleaner(BaseCleaner):
    def prepare(self):
        self.prepared = True
    def finish(self):
        self.finished = True
    def clean(self):
        raise OSError("Test failure")

def test_clean_removes_everything(tmp_path):
    temp_dir = tmp_path/"Temp"
    temp_dir.mkdir()
    temp_file = temp_dir/"test.txt"
    temp_file.write_text("test")
    cleaner = BaseCleaner(temp_dir,"Temp")
    cleaner.clean()

    assert not temp_file.exists()
    assert temp_dir.exists()
    assert cleaner.deleted == 1
    assert cleaner.skipped == 0

def test_run_removes_everything(tmp_path):
    temp_dir = tmp_path / "Temp"
    temp_dir.mkdir()
    temp_file = temp_dir / "test.txt"
    temp_file.write_text("test")
    cleaner = BaseCleaner(temp_dir, "Temp")
    cleaner.run()

    assert not temp_file.exists()
    assert temp_dir.exists()
    assert cleaner.deleted == 1
    assert cleaner.skipped == 0

def test_run_calls_finish_on_error(tmp_path):
    temp_dir = tmp_path / "Temp"
    temp_dir.mkdir()
    fake_cleaner = FakeCleaner(temp_dir, "Temp")
    with pytest.raises(OSError):
        fake_cleaner.run()
    assert fake_cleaner.prepared
    assert fake_cleaner.finished

def test_temp_cleaner_cleans_temp_folder(tmp_path):
    temp_dir = tmp_path / "Temp"
    temp_dir.mkdir()
    temp_file = temp_dir / "test.txt"
    temp_file.write_text("test")
    temp_cleaner = TempCleaner(temp_dir)
    temp_cleaner.clean()

    assert not temp_file.exists()
    assert temp_dir.exists()
    assert temp_cleaner.deleted == 1
    assert temp_cleaner.skipped == 0

def test_prefetch_cleaner_cleans_prefetch_folder(tmp_path):
    prefetch_dir = tmp_path / "Prefetch"
    prefetch_dir.mkdir()
    prefetch_file = prefetch_dir / "test.txt"
    prefetch_file.write_text("test")
    prefetch_cleaner = PrefetchCleaner(prefetch_dir)
    prefetch_cleaner.clean()

    assert not  prefetch_file.exists()
    assert prefetch_dir.exists()
    assert prefetch_cleaner.deleted == 1
    assert prefetch_cleaner.skipped == 0

class FakeSoftwareDistributionCleaner(SoftwareDistributionCleaner):
    def __init__(self, path: pathlib.Path):
        super().__init__(path)
        self.calls = []

    def _service(self, action, name):
        self.calls.append([action,name])

def test_software_distribution_stops_and_starts_services(tmp_path):
    download_dir = tmp_path / "Download"
    download_dir.mkdir()
    download_file = download_dir / "test.txt"
    download_file.write_text("test")
    software_cleaner = FakeSoftwareDistributionCleaner(download_dir)
    software_cleaner.run()

    assert not download_file.exists()
    assert software_cleaner.calls == [['stop', 'wuauserv'], ['stop', 'bits'], ['start', 'bits'], ['start', 'wuauserv']]

