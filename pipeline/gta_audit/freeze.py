"""The method lock: SHA-256 over model_frozen.json + model.py, with the lock time in ET."""
import datetime
import hashlib
import json
import os
import platform
from zoneinfo import ZoneInfo

from .errors import FreezeError

ET = ZoneInfo("America/New_York")


def method_hash(config_path, model_path):
    h = hashlib.sha256()
    for path in (config_path, model_path):
        if not os.path.isfile(path):
            raise FreezeError(f"cannot hash {path}: file missing")
        with open(path, "rb") as fh:
            data = fh.read()
        h.update(os.path.basename(path).encode() + b"\0" + str(len(data)).encode() + b"\0" + data)
    return h.hexdigest()


def freeze(config_path, model_path, lock_path, now=None):
    """Write the lock. Refuses to overwrite an existing lock: re-locking would void the pre-launch claim."""
    if os.path.exists(lock_path):
        raise FreezeError(f"{lock_path} already exists; the method is already locked. "
                          "Re-freezing is not allowed by the pipeline (delete the lock by hand only "
                          "with Cooper's explicit decision, and report it).")
    now = (now or datetime.datetime.now(tz=ET)).astimezone(ET)
    lock = {
        "sha256": method_hash(config_path, model_path),
        "files": [os.path.basename(config_path), os.path.basename(model_path)],
        "locked_at_et": now.isoformat(timespec="seconds"),
        "locked_at_display": f"{now.strftime('%b')} {now.day}, {now.year} "
                             f"{now.strftime('%I:%M %p').lstrip('0')} ET",
        "python_version": platform.python_version(),
    }
    with open(lock_path, "w", encoding="utf-8") as fh:
        json.dump(lock, fh, indent=2)
        fh.write("\n")
    return lock


def verify(config_path, model_path, lock_path):
    """Return the lock if config + model still match it; otherwise raise FreezeError."""
    if not os.path.isfile(lock_path):
        raise FreezeError(f"no lock at {lock_path}: run `run.py freeze` first")
    with open(lock_path, encoding="utf-8") as fh:
        lock = json.load(fh)
    current = method_hash(config_path, model_path)
    if current != lock.get("sha256"):
        raise FreezeError(f"frozen method changed since {lock.get('locked_at_et')}: "
                          f"lock sha256 {lock.get('sha256', '')[:12]} != current {current[:12]}")
    return lock
