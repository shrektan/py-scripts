import pathlib

def simplify(tgt: str, rm_empty_folder: bool):
    target = pathlib.Path(tgt)
    for entry in target.iterdir():
        if entry.is_dir():
            for f in entry.iterdir():
                if f.name == ".DS_Store":
                    f.unlink()
                    continue
                fname = f.name
                while (dest := target / fname).exists():
                    fname = "0_" + fname
                f.rename(dest)
            if rm_empty_folder:
                entry.rmdir()


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
