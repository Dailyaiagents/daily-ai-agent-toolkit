from __future__ import annotations

import importlib.util
import io
import stat
import tarfile
import zipfile
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "verify_release", ROOT / "scripts" / "verify-release.py"
)
assert SPEC and SPEC.loader
VERIFY_RELEASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY_RELEASE)


def test_wheel_symlink_is_rejected(tmp_path: Path) -> None:
    wheel = tmp_path / "unsafe.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        item = zipfile.ZipInfo("package/link")
        item.create_system = 3
        item.external_attr = (stat.S_IFLNK | 0o777) << 16
        archive.writestr(item, "target")
    with pytest.raises(ValueError, match="unsafe zip member type"):
        VERIFY_RELEASE.inspect_archive(wheel)


def test_sdist_link_is_rejected(tmp_path: Path) -> None:
    archive_path = tmp_path / "unsafe.tar.gz"
    with tarfile.open(archive_path, "w:gz") as archive:
        regular = tarfile.TarInfo("package/data.txt")
        data = b"safe"
        regular.size = len(data)
        archive.addfile(regular, io.BytesIO(data))
        link = tarfile.TarInfo("package/link")
        link.type = tarfile.SYMTYPE
        link.linkname = "data.txt"
        archive.addfile(link)
    with pytest.raises(ValueError, match="unsafe tar member type"):
        VERIFY_RELEASE.inspect_archive(archive_path)
