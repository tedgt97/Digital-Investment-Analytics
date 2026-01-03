from __future__ import annotations
import json
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

EASTERN_TZ = ZoneInfo('US/Eastern')

def _get_repo_root() -> Path:
    """Return the repository root directory (one level above 'src')."""
    return Path(__file__).resolve().parents[2]

def _get_window_start(dt: datetime) -> datetime:
    """
    Compute the start of the current FMP daily window in US/Eastern.
    FMP resets quotas every day at 3 PM Eastern.
    """
    dt_eastern = dt.astimezone(EASTERN_TZ)
    reset_today = dt_eastern.replace(hour=15, minute=0, second=0, microsecond=0)

    if dt_eastern < reset_today:
        # Before today's 3 PM: still in the window that started yesterday at 3 PM.
        window_date = dt_eastern.date()
    else:
        # After today's 3 PM: window starts today at 3 PM.
        window_date = dt_eastern.date()

    return datetime.combine(window_date, time(15, 0), tzinfo=EASTERN_TZ)  # --Fixed--

@dataclass
class UsageState:
    window_start: datetime
    count: int

class FMPUsageTracker:
    """Persist and manage daily FMP API usage across processes."""

    def __init__(self, storage_path: Optional[Path] = None) -> None:
        self.repo_root = _get_repo_root()
        self.storage_path = storage_path or (self.repo_root / "config" / "fmp_usage.json")
        self.state: UsageState = self._load_state()

    def _load_state(self) -> UsageState:
        """Load usage stae from disk, resetting if the window has changed."""
        now = datetime.now(tz=EASTERN_TZ)
        current_window_start = _get_window_start(now)

        if not self.storage_path.exists():
            return UsageState(window_start=current_window_start, count=0)
        
        try:
            with self.storage_path.open("r", encoding='utf-8') as f:
                raw = json.load(f)
            stored_window_start = datetime.fromisoformat(raw.get('window_start'))
            stored_count = int(raw.get('count', 0))
        except Exception:
            # If anything goes wrong, start fresh for the current window.
            return UsageState(window_start=current_window_start, count=0)
        
        # If the stored window is the same as the current window, keep the count.
        if _get_window_start(stored_window_start) == current_window_start:
            return UsageState(window_start=current_window_start, count=stored_count)
        
        # Otherwise, new daily window -> reset count.
        return UsageState(window_start=current_window_start, count=0)
    
    def _persist(self) -> None:
        """Write current state to disk."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            'window_start': self.state.window_start.isoformat(),
            'count': self.state.count,
        }
        with self.storage_path.open("w", encoding='utf-8') as f:
            json.dump(payload, f, indent=2)

    @property
    def count(self) -> int:
        return self.state.count
    
    def increment(self) -> None:
        """Increment the count for the current window and persist."""
        now = datetime.now(tz=EASTERN_TZ)
        current_window_start = _get_window_start(now)

        # If we crossed into a new window since last use, reset first.
        if current_window_start != self.state.window_start:
            self.state = UsageState(window_start=current_window_start, count=0)
        
        self.state.count += 1
        self._persist()
    
    def remaining(self, daily_limit: int) -> int:
        """Return remaining quota in the current daily window."""
        return max(daily_limit - self.state.count, 0)

