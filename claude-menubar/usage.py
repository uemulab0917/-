"""
Claude Code usage reader.

Scans ~/.claude/projects/ for recent API calls and calculates
token usage within the rolling 5-hour rate-limit window.
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

CLAUDE_HOME = Path.home() / ".claude"
PROJECTS_DIR = CLAUDE_HOME / "projects"
CONFIG_FILE = CLAUDE_HOME / "menubar.json"

BLOCK_HOURS = 5
DEFAULT_MAX_TOKENS = 88000  # Conservative Pro plan estimate; override in ~/.claude/menubar.json


def _load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _parse_timestamp(entry: dict) -> "datetime | None":
    """Extract a UTC datetime from various entry shapes."""
    for key in ("timestamp", "ts", "created", "created_at", "time"):
        val = entry.get(key)
        if val is None:
            continue
        if isinstance(val, (int, float)):
            return datetime.fromtimestamp(val, tz=timezone.utc)
        if isinstance(val, str):
            try:
                return datetime.fromisoformat(val.replace("Z", "+00:00"))
            except ValueError:
                pass
    return None


def _extract_tokens(entry: dict) -> int:
    """Return total tokens (input + output + cache) from an entry."""
    usage = None

    if "usage" in entry:
        usage = entry["usage"]
    elif isinstance(entry.get("message"), dict):
        usage = entry["message"].get("usage")

    if not isinstance(usage, dict):
        return 0

    return (
        usage.get("input_tokens", 0)
        + usage.get("output_tokens", 0)
        + usage.get("cache_creation_input_tokens", 0)
        + usage.get("cache_read_input_tokens", 0)
    )


def _scan_entries(cutoff: datetime) -> list[tuple[datetime, int]]:
    """Return (timestamp, tokens) pairs for entries after *cutoff*."""
    entries: list[tuple[datetime, int]] = []

    if not PROJECTS_DIR.exists():
        return entries

    for project_dir in PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        for f in project_dir.iterdir():
            if f.suffix not in (".jsonl", ".json"):
                continue
            try:
                with open(f, encoding="utf-8") as fp:
                    for line in fp:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            obj = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        ts = _parse_timestamp(obj)
                        if ts is None or ts < cutoff:
                            continue
                        tokens = _extract_tokens(obj)
                        if tokens > 0:
                            entries.append((ts, tokens))
            except (OSError, IOError):
                continue

    return entries


def get_usage() -> dict:
    """
    Return a dict describing current 5-hour block usage:

    {
        "percent": int,               # 0-100
        "used_tokens": int,
        "max_tokens": int,
        "block_remaining": timedelta, # time until oldest entry expires
        "rate_limited": bool,
        "wait_remaining": timedelta | None,
        "error": str | None,
    }
    """
    cfg = _load_config()
    max_tokens = int(cfg.get("max_tokens", DEFAULT_MAX_TOKENS))
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=BLOCK_HOURS)

    try:
        entries = _scan_entries(cutoff)
    except Exception as exc:
        return {
            "percent": 0,
            "used_tokens": 0,
            "max_tokens": max_tokens,
            "block_remaining": timedelta(hours=BLOCK_HOURS),
            "rate_limited": False,
            "wait_remaining": None,
            "error": str(exc),
        }

    if not entries:
        return {
            "percent": 0,
            "used_tokens": 0,
            "max_tokens": max_tokens,
            "block_remaining": timedelta(hours=BLOCK_HOURS),
            "rate_limited": False,
            "wait_remaining": None,
            "error": None,
        }

    entries.sort(key=lambda x: x[0])
    used_tokens = sum(t for _, t in entries)
    percent = min(100, round(used_tokens / max_tokens * 100))

    # Block resets when the oldest entry rolls off the 5-hour window
    oldest_ts = entries[0][0]
    block_end = oldest_ts + timedelta(hours=BLOCK_HOURS)
    block_remaining = max(timedelta(0), block_end - now)

    rate_limited = percent >= 100
    wait_remaining = block_remaining if rate_limited else None

    return {
        "percent": percent,
        "used_tokens": used_tokens,
        "max_tokens": max_tokens,
        "block_remaining": block_remaining,
        "rate_limited": rate_limited,
        "wait_remaining": wait_remaining,
        "error": None,
    }
