"""Safe writing of approved documentation with backups."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile

from doc_sync.security import is_secret_path


def safe_write_document(path: str | Path, content: str, *, approved: bool = False, fingerprint: str | None = None) -> dict[str, str]:
    """Write content atomically after approval, retaining only the latest backup."""
    target = Path(path)
    if is_secret_path(target):
        raise ValueError(f"Refusing to write secret-like target: {target}")
    if not approved:
        raise ValueError("write requires approval before any update")

    backup_path = target.with_name(f"{target.name}.bak")
    if target.exists():
        shutil.copy2(target, backup_path)

    temp_path = None
    try:
        with NamedTemporaryFile("w", delete=False, dir=str(target.parent), encoding="utf-8") as handle:
            temp_path = Path(handle.name)
            handle.write(content)
        os.replace(temp_path, target)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink(missing_ok=True)

    return {"target": str(target), "backup": str(backup_path)}
