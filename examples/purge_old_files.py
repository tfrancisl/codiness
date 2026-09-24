import logging
import os
import time

log = logging.getLogger(__name__)


def purge_old_files(directory: str, max_age_days: int = 30) -> int:
    """Permanently delete files older than max_age_days. Returns how many were removed."""
    cutoff = time.time() - max_age_days * 86400
    removed = 0
    for entry in os.scandir(directory):
        if entry.is_file() and entry.stat().st_mtime < cutoff:
            os.remove(entry.path)
            log.warning("deleted %s", entry.path)
            removed += 1
    return removed
