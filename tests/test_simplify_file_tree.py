from simplify_file_tree import simplify

def test_simiplify(tmp_path):
    (tmp_path / "file1").touch()
    (tmp_path / "folder").mkdir()
    (tmp_path / "folder" / "folder").touch()
    (tmp_path / "folder" / "file2").touch()
    (tmp_path / "folder" / "folder2").mkdir()
    simplify(str(tmp_path), True)
    files = [f for f in tmp_path.iterdir()]
    assert len(files) == 4
    assert (tmp_path / "file1") in files
    assert (tmp_path / "file2") in files
    assert (tmp_path / "0_folder") in files
    assert (tmp_path / "folder2") in files
