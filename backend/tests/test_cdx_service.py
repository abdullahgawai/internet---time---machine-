import pytest
import os
import tempfile
from app.services.cdx_service import normalize_url, format_timestamp, CDXService
from app.models import SnapshotItem

def test_normalize_url():
    assert normalize_url("https://www.apple.com/") == "apple.com"
    assert normalize_url("http://apple.com/subpath/") == "apple.com/subpath/"
    assert normalize_url("GOOGLE.COM#about") == "google.com"
    assert normalize_url("  https://archive.org  ") == "archive.org"

def test_format_timestamp():
    year, dt_str = format_timestamp("19961022105458")
    assert year == 1996
    assert dt_str == "1996-10-22 10:54:58"

    year, dt_str = format_timestamp("20000101")
    assert year == 2000
    assert dt_str == "2000-01-01 00:00:00"

def test_group_years():
    snaps = [
        SnapshotItem(
            timestamp="19990101120000",
            year=1999,
            date="1999-01-01 12:00:00",
            playback_url="https://web.archive.org/web/19990101120000/http://example.com",
            clean_playback_url="https://web.archive.org/web/19990101120000id_/http://example.com"
        ),
        SnapshotItem(
            timestamp="19990601120000",
            year=1999,
            date="1999-06-01 12:00:00",
            playback_url="https://web.archive.org/web/19990601120000/http://example.com",
            clean_playback_url="https://web.archive.org/web/19990601120000id_/http://example.com"
        ),
        SnapshotItem(
            timestamp="20050515120000",
            year=2005,
            date="2005-05-15 12:00:00",
            playback_url="https://web.archive.org/web/20050515120000/http://example.com",
            clean_playback_url="https://web.archive.org/web/20050515120000id_/http://example.com"
        )
    ]
    years = CDXService._group_years(snaps)
    assert len(years) == 2
    assert years[0].year == 1999
    assert years[0].count == 2
    assert years[1].year == 2005
    assert years[1].count == 1
