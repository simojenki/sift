import subprocess
import sys
from pathlib import Path

from sift import discover_files, move_files

SIFT = Path(__file__).parent.parent / "src" / "sift"


def test_smoke(tmp_path):
    src = tmp_path / "src"
    dest = tmp_path / "dest"
    src.mkdir()
    dest.mkdir()
    result = subprocess.run([sys.executable, SIFT, str(src), str(dest)])
    assert result.returncode == 0


def test_discover_empty_dir(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    assert discover_files(src) == []


def test_discover_flat_dir(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("a")
    (src / "b.txt").write_text("b")
    found = {p.name for p in discover_files(src)}
    assert found == {"a.txt", "b.txt"}


def test_discover_nested_dir(tmp_path):
    src = tmp_path / "src"
    (src / "sub").mkdir(parents=True)
    (src / "top.txt").write_text("t")
    (src / "sub" / "deep.txt").write_text("d")
    found = {p.relative_to(src) for p in discover_files(src)}
    assert found == {Path("top.txt"), Path("sub/deep.txt")}


def test_move_flat(tmp_path):
    src = tmp_path / "src"
    dest = tmp_path / "dest"
    src.mkdir()
    dest.mkdir()
    (src / "file.txt").write_text("hello")
    move_files(src, dest)
    assert (dest / "file.txt").read_text() == "hello"
    assert not (src / "file.txt").exists()


def test_move_preserves_structure(tmp_path):
    src = tmp_path / "src"
    dest = tmp_path / "dest"
    (src / "a" / "b").mkdir(parents=True)
    dest.mkdir()
    (src / "a" / "b" / "deep.txt").write_text("deep")
    move_files(src, dest)
    assert (dest / "a" / "b" / "deep.txt").read_text() == "deep"
    assert not (src / "a" / "b" / "deep.txt").exists()


def test_skip_existing_file(tmp_path):
    src = tmp_path / "src"
    dest = tmp_path / "dest"
    src.mkdir()
    dest.mkdir()
    (src / "file.txt").write_text("new")
    (dest / "file.txt").write_text("original")
    move_files(src, dest)
    assert (dest / "file.txt").read_text() == "original"
    assert (src / "file.txt").exists()


def test_skip_existing_moves_others(tmp_path):
    src = tmp_path / "src"
    dest = tmp_path / "dest"
    src.mkdir()
    dest.mkdir()
    (src / "kept.txt").write_text("new")
    (src / "moved.txt").write_text("move me")
    (dest / "kept.txt").write_text("original")
    move_files(src, dest)
    assert (dest / "kept.txt").read_text() == "original"
    assert (src / "kept.txt").exists()
    assert (dest / "moved.txt").read_text() == "move me"
    assert not (src / "moved.txt").exists()
