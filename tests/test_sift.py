import subprocess
import sys
from pathlib import Path

from sift import SiftRecord, SiftRecords, discover_files, hash_file, move_files


SIFT = Path(__file__).parent.parent / "src" / "sift"


def test_smoke(tmp_path):
    src = tmp_path / "src"
    dest = tmp_path / "dest"
    src.mkdir()
    dest.mkdir()
    result = subprocess.run([sys.executable, SIFT, str(src), str(dest)])
    assert result.returncode == 0


EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_hash_file_same_content(tmp_path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("hello")
    b.write_text("hello")
    assert hash_file(a) == hash_file(b)


def test_hash_file_different_content(tmp_path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("hello")
    b.write_text("world")
    assert hash_file(a) != hash_file(b)


def test_hash_file_empty(tmp_path):
    f = tmp_path / "empty.txt"
    f.write_bytes(b"")
    assert hash_file(f) == EMPTY_SHA256


def test_sift_records_get_missing_db(tmp_path):
    store = SiftRecords(tmp_path)
    assert store.get("abc123") is None


def test_sift_records_insert_then_get(tmp_path):
    record = SiftRecord(hash="abc123", filename="file.txt", first_seen="2026-01-01T00:00:00+00:00")
    with SiftRecords(tmp_path) as store:
        store.insert(record)
        assert store.get("abc123") == record


def test_sift_records_get_unknown_hash(tmp_path):
    with SiftRecords(tmp_path) as store:
        store.insert(SiftRecord(hash="aaa", filename="a.txt", first_seen="2026-01-01T00:00:00+00:00"))
        assert store.get("bbb") is None


def test_sift_records_duplicate_insert_no_error(tmp_path):
    with SiftRecords(tmp_path) as store:
        record = SiftRecord(hash="abc123", filename="file.txt", first_seen="2026-01-01T00:00:00+00:00")
        store.insert(record)
        store.insert(record)


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


def test_skip_duplicate_content_different_path(tmp_path):
    src1 = tmp_path / "src1"
    src2 = tmp_path / "src2"
    dest = tmp_path / "dest"
    src1.mkdir()
    src2.mkdir()
    dest.mkdir()
    (src1 / "a.txt").write_text("same content")
    (src2 / "b.txt").write_text("same content")
    move_files(src1, dest)
    move_files(src2, dest)
    assert (dest / "a.txt").exists()
    assert (src2 / "b.txt").exists()


def test_hash_file_created_after_move(tmp_path):
    src = tmp_path / "src"
    dest = tmp_path / "dest"
    src.mkdir()
    dest.mkdir()
    (src / "file.txt").write_text("content")
    move_files(src, dest)
    assert (dest / ".sift.db").exists()


def test_hash_file_not_created_when_nothing_moved(tmp_path):
    src = tmp_path / "src"
    dest = tmp_path / "dest"
    src.mkdir()
    dest.mkdir()
    move_files(src, dest)
    assert not (dest / ".sift.db").exists()


def test_hash_persists_across_runs(tmp_path):
    src1 = tmp_path / "src1"
    src2 = tmp_path / "src2"
    dest = tmp_path / "dest"
    src1.mkdir()
    src2.mkdir()
    dest.mkdir()
    (src1 / "original.txt").write_text("unique content")
    move_files(src1, dest)
    (src2 / "copy.txt").write_text("unique content")
    move_files(src2, dest)
    assert (src2 / "copy.txt").exists()


def test_log_move(tmp_path):
    src, dest = tmp_path / "src", tmp_path / "dest"
    src.mkdir()
    dest.mkdir()
    (src / "file.txt").write_text("hello")
    messages = []
    move_files(src, dest, log=messages.append)
    assert messages == ["+ file.txt"]


def test_log_existing_path(tmp_path):
    src, dest = tmp_path / "src", tmp_path / "dest"
    src.mkdir()
    dest.mkdir()
    (src / "file.txt").write_text("new")
    (dest / "file.txt").write_text("original")
    messages = []
    move_files(src, dest, log=messages.append)
    assert messages == ["! file.txt"]


def test_log_duplicate_hash(tmp_path):
    src1, src2, dest = tmp_path / "src1", tmp_path / "src2", tmp_path / "dest"
    src1.mkdir()
    src2.mkdir()
    dest.mkdir()
    (src1 / "a.txt").write_text("same")
    (src2 / "b.txt").write_text("same")
    move_files(src1, dest)
    messages = []
    move_files(src2, dest, log=messages.append)
    assert len(messages) == 1
    assert messages[0].startswith("!! b.txt (")
    assert "a.txt" in messages[0]


def test_concurrent_workers_correct(tmp_path):
    src, dest = tmp_path / "src", tmp_path / "dest"
    src.mkdir()
    dest.mkdir()
    for i in range(6):
        (src / f"file{i}.txt").write_text(f"content {i}")
    (src / "dup.txt").write_text("content 0")
    messages = []
    move_files(src, dest, log=messages.append, workers=3)
    moved = [m for m in messages if m.startswith("+")]
    skipped_hash = [m for m in messages if m.startswith("!!")]
    assert len(moved) == 6
    assert len(skipped_hash) == 1


def test_log_silent_by_default(tmp_path):
    import io
    import sys

    src, dest = tmp_path / "src", tmp_path / "dest"
    src.mkdir()
    dest.mkdir()
    (src / "file.txt").write_text("hello")
    captured = io.StringIO()
    sys.stdout = captured
    move_files(src, dest)
    sys.stdout = sys.__stdout__
    assert captured.getvalue() == ""
