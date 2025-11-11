import asyncio
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

from defusedxml.ElementTree import fromstring as safe_xml_fromstring

import fcntl

from src.core.config import config

BASE_DIR = Path(getattr(config.static, "BASE_DIR", Path.cwd() / "storage")).resolve()
os.makedirs(BASE_DIR, exist_ok=True)

MAX_UPLOAD_SIZE = getattr(config.static, "MAX_UPLOAD_SIZE", 20 * 1024 * 1024)
MAX_FILENAME_LENGTH = getattr(config.static, "FILE_NAME_MAX_LENGTH", 255)
ZIP_MAX_TOTAL_EXTRACTED_SIZE = getattr(
    config.static, "ZIP_MAX_TOTAL_EXTRACTED_SIZE", 200 * 1024 * 1024
)
ZIP_MAX_RATIO = getattr(config.static, "ZIP_MAX_RATIO", 100)
ZIP_MAX_FILES = getattr(config.static, "ZIP_MAX_FILES", 1000)

_LOCKS = {}


def ensure_valid_filename(name: str) -> str:
    name = os.path.basename(name)
    if len(name) > MAX_FILENAME_LENGTH:
        raise ValueError("filename too long")
    return name


def resolve_secure_path(relpath: str) -> Path:
    safe_name = os.path.normpath(relpath)
    candidate = (BASE_DIR / safe_name).resolve()
    if not str(candidate).startswith(str(BASE_DIR)):
        raise PermissionError("Path traversal detected")
    return candidate


def safe_load_json(data: str):
    return json.loads(data)


def safe_load_xml(data: str):
    return safe_xml_fromstring(data)


class AtomicWriter:
    def __init__(self, target: Path, mode="wb"):
        self.target = target
        self.mode = mode
        self.temp_path = None
        self._fh = None

    def __enter__(self):
        parent = self.target.parent
        parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(parent))
        os.close(fd)
        self.temp_path = Path(tmp)
        self._fh = open(self.temp_path, self.mode)
        fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX)
        return self._fh

    def __exit__(self, exc_type, *_):
        if self._fh:
            fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
            self._fh.close()
        if exc_type:
            try:
                self.temp_path.unlink(missing_ok=True)
            except Exception:
                pass
        else:
            os.replace(str(self.temp_path), str(self.target))


def acquire_lock_for_path(p: Path):
    if str(p) not in _LOCKS:
        _LOCKS[str(p)] = asyncio.Lock()
    return _LOCKS[str(p)]


def inspect_zip_safety(zf: zipfile.ZipFile):
    total_uncompressed = 0
    total_compressed = 0
    nfiles = 0
    for info in zf.infolist():
        nfiles += 1
        total_uncompressed += info.file_size
        total_compressed += info.compress_size or 0
        if (
            info.compress_size
            and info.file_size / max(1, info.compress_size) > ZIP_MAX_RATIO
        ):
            raise ValueError(f"Suspicious compression ratio: {info.filename}")
    if nfiles > ZIP_MAX_FILES:
        raise ValueError("Too many files in zip")
    if total_uncompressed > ZIP_MAX_TOTAL_EXTRACTED_SIZE:
        raise ValueError("Total extracted size too large")
