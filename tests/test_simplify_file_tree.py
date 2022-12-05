from simplify_file_tree import simplify

def test_simiplify(tmp_path):
    (tmp_path / "file1").touch()
    (tmp_path / "folder1").mkdir()
    (tmp_path / "folder1" / "folder1").touch()
    (tmp_path / "folder1" / "file2").touch()
    (tmp_path / "folder1" / "folder2").mkdir()
    (tmp_path / "folder3").mkdir()
    (tmp_path / "folder3" / "file1").touch()
    (tmp_path / "folder4").mkdir()
    (tmp_path / "folder4" / "file1").touch()
    simplify(str(tmp_path), True)
    files = list(tmp_path.iterdir())
    assert len(files) == 6
    assert (tmp_path / "file1") in files
    assert (tmp_path / "file2") in files
    assert (tmp_path / "0_folder1") in files
    assert (tmp_path / "folder2") in files
    assert (tmp_path / "0_file1") in files
    assert (tmp_path / "0_0_file1") in files
