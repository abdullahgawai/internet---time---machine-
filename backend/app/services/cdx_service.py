import re
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Tuple
import httpx

from app.database import get_db
from app.models import SnapshotItem, YearDensity, SnapshotsResponse

logger = logging.getLogger(__name__)

CDX_API_URL = "https://web.archive.org/cdx/search/cdx"
WAYBACK_PLAYBACK_BASE = "https://web.archive.org/web"
CACHE_TTL_DAYS = 7
USER_AGENT = "InternetTimeMachine/1.0 (Digital Archaeology Educational Tool; https://archive.org)"

def normalize_url(url: str) -> str:
    """
    Normalize user submitted URL by trimming whitespace,
    removing protocol, leading www, trailing slashes, and anchors.
    """
    cleaned = url.strip()
    # Remove protocol
    cleaned = re.sub(r"^https?://", "", cleaned, flags=re.IGNORECASE)
    # Remove leading www. for uniform matching (though keep path intact)
    if cleaned.lower().startswith("www."):
        cleaned = cleaned[4:]
    # Remove hash/anchor
    cleaned = cleaned.split("#")[0]
    # Remove trailing slash if it's just the domain
    if cleaned.endswith("/") and "/" not in cleaned[:-1]:
        cleaned = cleaned[:-1]
    return cleaned.lower()

def format_timestamp(ts: str) -> Tuple[int, str]:
    """Parse YYYYMMDDHHMMSS into (year, 'YYYY-MM-DD HH:MM:SS')."""
    ts_str = str(ts).ljust(14, '0')[:14]
    year = int(ts_str[:4])
    month = ts_str[4:6]
    day = ts_str[6:8]
    hour = ts_str[8:10]
    minute = ts_str[10:12]
    second = ts_str[12:14]
    formatted = f"{year}-{month}-{day} {hour}:{minute}:{second}"
    return year, formatted

class CDXService:
    @staticmethod
    async def get_snapshots_from_cache(normalized_url: str) -> Optional[List[SnapshotItem]]:
        """Check if snapshots exist in SQLite cache and are still fresh (within 7 days)."""
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT last_fetched_at FROM snapshot_cache_meta WHERE url = ?",
                (normalized_url,)
            )
            row = await cursor.fetchone()
            if not row:
                return None
            
            # Check TTL
            try:
                last_fetched = datetime.fromisoformat(row["last_fetched_at"].replace("Z", "+00:00"))
                # If naive, assume UTC
                if last_fetched.tzinfo is None:
                    last_fetched = last_fetched.replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                if now - last_fetched > timedelta(days=CACHE_TTL_DAYS):
                    return None # Cache expired
            except Exception:
                # If parsing fails, fall back to re-fetching
                return None

            # Fetch cached records
            cursor = await db.execute(
                """SELECT timestamp, status_code, mimetype, length 
                   FROM snapshots 
                   WHERE url = ? 
                   ORDER BY timestamp ASC""",
                (normalized_url,)
            )
            rows = await cursor.fetchall()
            if not rows:
                return []

            items = []
            for r in rows:
                ts = r["timestamp"]
                yr, dt_str = format_timestamp(ts)
                items.append(
                    SnapshotItem(
                        timestamp=ts,
                        year=yr,
                        date=dt_str,
                        status_code=r["status_code"],
                        mimetype=r["mimetype"],
                        length=r["length"],
                        playback_url=f"{WAYBACK_PLAYBACK_BASE}/{ts}/http://{normalized_url}",
                        clean_playback_url=f"{WAYBACK_PLAYBACK_BASE}/{ts}id_/http://{normalized_url}"
                    )
                )
            return items

    @staticmethod
    async def save_snapshots_to_cache(normalized_url: str, snapshots: List[Dict]):
        """Persist snapshot list to SQLite and update cache metadata."""
        async with get_db() as db:
            # Upsert cache metadata
            now_iso = datetime.now(timezone.utc).isoformat()
            await db.execute(
                """INSERT INTO snapshot_cache_meta (url, last_fetched_at, total_count)
                   VALUES (?, ?, ?)
                   ON CONFLICT(url) DO UPDATE SET last_fetched_at = excluded.last_fetched_at, total_count = excluded.total_count""",
                (normalized_url, now_iso, len(snapshots))
            )

            # Insert snapshots
            for s in snapshots:
                await db.execute(
                    """INSERT OR IGNORE INTO snapshots (url, timestamp, status_code, mimetype, length)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        normalized_url,
                        s["timestamp"],
                        s.get("status_code", 200),
                        s.get("mimetype", "text/html"),
                        s.get("length", 0)
                    )
                )
            await db.commit()

    @classmethod
    async def fetch_snapshots(cls, raw_url: str) -> SnapshotsResponse:
        """Fetch snapshots for a given URL with caching, rate-limit backoff, and grouping."""
        norm_url = normalize_url(raw_url)
        if not norm_url or "." not in norm_url:
            return SnapshotsResponse(
                url=raw_url,
                normalized_url=norm_url,
                total_snapshots=0,
                years=[],
                snapshots=[],
                cached=False,
                message="Invalid domain or URL format."
            )

        # 1. Check cache first
        cached_items = await cls.get_snapshots_from_cache(norm_url)
        if cached_items is not None:
            years = cls._group_years(cached_items)
            return SnapshotsResponse(
                url=raw_url,
                normalized_url=norm_url,
                total_snapshots=len(cached_items),
                years=years,
                snapshots=cached_items,
                cached=True,
                message="Retrieved from local cache." if cached_items else "No snapshots found in archive."
            )

        # 2. Query CDX API with exponential backoff
        params = {
            "url": norm_url,
            "output": "json",
            "fl": "timestamp,original,mimetype,statuscode,length",
            "filter": ["statuscode:200", "mimetype:text/html"],
            "collapse": "timestamp:6", # 1 capture per month max -> responsive & avoids CDX 504 timeouts
            "limit": "5000"
        }
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json"
        }

        retries = 3
        backoff_delay = 1.0
        data = None

        async with httpx.AsyncClient(timeout=35.0, follow_redirects=True) as client:
            for attempt in range(retries):
                try:
                    res = await client.get(CDX_API_URL, params=params, headers=headers)
                    if res.status_code == 200:
                        try:
                            data = res.json()
                        except Exception:
                            logger.warning("Failed to parse CDX JSON: %s", res.text[:200])
                            data = []
                        break
                    elif res.status_code in (429, 503, 504):
                        logger.warning("CDX API returned %s. Retrying in %ss (attempt %s/%s)...", res.status_code, backoff_delay, attempt + 1, retries)
                        await asyncio.sleep(backoff_delay)
                        backoff_delay *= 2
                    else:
                        logger.warning("CDX API error status %s: %s", res.status_code, res.text[:200])
                        break
                except httpx.RequestError as exc:
                    logger.warning("CDX request failed: %s. Retrying in %ss...", repr(exc), backoff_delay)
                    await asyncio.sleep(backoff_delay)
                    backoff_delay *= 2

        raw_snapshots: List[Dict] = []
        if data and len(data) > 1:
            header = data[0]
            # Mapping indices
            ts_idx = header.index("timestamp") if "timestamp" in header else 0
            mime_idx = header.index("mimetype") if "mimetype" in header else 2
            status_idx = header.index("statuscode") if "statuscode" in header else 3
            len_idx = header.index("length") if "length" in header else 4

            for row in data[1:]:
                if len(row) > ts_idx:
                    ts = str(row[ts_idx])
                    mime = str(row[mime_idx]) if len(row) > mime_idx else "text/html"
                    status = int(row[status_idx]) if len(row) > status_idx and str(row[status_idx]).isdigit() else 200
                    length = int(row[len_idx]) if len(row) > len_idx and str(row[len_idx]).isdigit() else 0
                    raw_snapshots.append({
                        "timestamp": ts,
                        "status_code": status,
                        "mimetype": mime,
                        "length": length
                    })

        # 3. Save to cache — but only if the CDX API actually responded.
        #    If data is None (all retries failed), don't cache the empty result
        #    so the next request will retry the CDX call instead of returning
        #    a cached empty list.
        if data is not None:
            await cls.save_snapshots_to_cache(norm_url, raw_snapshots)

        # 4. Transform into response items
        items: List[SnapshotItem] = []
        for s in raw_snapshots:
            ts = s["timestamp"]
            yr, dt_str = format_timestamp(ts)
            items.append(
                SnapshotItem(
                    timestamp=ts,
                    year=yr,
                    date=dt_str,
                    status_code=s["status_code"],
                    mimetype=s["mimetype"],
                    length=s["length"],
                    playback_url=f"{WAYBACK_PLAYBACK_BASE}/{ts}/http://{norm_url}",
                    clean_playback_url=f"{WAYBACK_PLAYBACK_BASE}/{ts}id_/http://{norm_url}"
                )
            )

        years = cls._group_years(items)
        msg = "Successfully fetched from Wayback Machine." if items else "No snapshots found for this domain."
        return SnapshotsResponse(
            url=raw_url,
            normalized_url=norm_url,
            total_snapshots=len(items),
            years=years,
            snapshots=items,
            cached=False,
            message=msg
        )

    @classmethod
    async def get_nearest_snapshot(cls, raw_url: str, target_ts: str) -> Optional[SnapshotItem]:
        """Find the snapshot closest in time to a given timestamp."""
        norm_url = normalize_url(raw_url)
        # Ensure we have snapshots loaded
        cached = await cls.get_snapshots_from_cache(norm_url)
        if cached is None:
            res = await cls.fetch_snapshots(raw_url)
            cached = res.snapshots

        if not cached:
            return None

        # Clean target_ts
        target_int = int(re.sub(r"\D", "", target_ts).ljust(14, '0')[:14])
        
        # Binary search or closest distance
        best_item = cached[0]
        best_diff = abs(int(best_item.timestamp) - target_int)

        for item in cached[1:]:
            diff = abs(int(item.timestamp) - target_int)
            if diff < best_diff:
                best_diff = diff
                best_item = item

        return best_item

    @staticmethod
    def _group_years(snapshots: List[SnapshotItem]) -> List[YearDensity]:
        """Aggregate snapshot counts and representative timestamps per calendar year."""
        year_map: Dict[int, List[SnapshotItem]] = {}
        for s in snapshots:
            year_map.setdefault(s.year, []).append(s)

        results: List[YearDensity] = []
        for yr in sorted(year_map.keys()):
            items = year_map[yr]
            # Pick representative snapshot (mid-year or closest to July)
            mid_idx = len(items) // 2
            rep = items[mid_idx]
            results.append(
                YearDensity(
                    year=yr,
                    count=len(items),
                    first_timestamp=items[0].timestamp,
                    last_timestamp=items[-1].timestamp,
                    representative_timestamp=rep.timestamp
                )
            )
        return results
