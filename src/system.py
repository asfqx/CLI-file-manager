import asyncio
import shutil
from pathlib import Path
from src.core.config import config
from src.core.databaseAccessor import db

BASE_DIR = Path(getattr(config.static, "BASE_DIR", Path.cwd() / "storage")).resolve()


async def disk_stats():
    """Возвращает информацию о доступных дисках"""
    drives = []
    try:
        usage = shutil.disk_usage(BASE_DIR)
        drives.append(
            {
                "path": str(BASE_DIR),
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
            }
        )
    except Exception:
        pass

    try:
        root_usage = shutil.disk_usage(Path("/"))
        drives.append(
            {
                "path": "/",
                "total": root_usage.total,
                "used": root_usage.used,
                "free": root_usage.free,
            }
        )
    except Exception:
        pass

    return drives


async def cmd_disk_stats(args=None):
    """Команда CLI: выводит статистику дисков"""
    stats = await disk_stats()
    for d in stats:
        total = d["total"]
        used = d["used"]
        free = d["free"]
        print(f"Path: {d['path']}  total={total} used={used} free={free}")
