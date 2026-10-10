import pytest
from Temp.TempCleaner import TempCleaner
from BaseCleaner.BaseCleaner import BaseCleaner

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