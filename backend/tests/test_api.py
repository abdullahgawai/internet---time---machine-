import pytest
import os
import tempfile
from fastapi.testclient import TestClient

# Set temporary database path for testing
test_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_PATH"] = test_db.name

from app.main import app

client = TestClient(app)

def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"

def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "healthy"}

def test_invalid_url_snapshots():
    res = client.get("/api/snapshots?url=")
    assert res.status_code == 400
    assert "error" in res.json()

def test_stubs_return_501():
    # /api/analyze
    res = client.post("/api/analyze", json={"url": "apple.com", "ts1": "19970101", "ts2": "20200101"})
    assert res.status_code == 501
    assert res.json()["error"]["code"] == "NOT_IMPLEMENTED"

    # /api/evolution-score
    res = client.get("/api/evolution-score?url=apple.com")
    assert res.status_code == 501
    assert res.json()["error"]["code"] == "NOT_IMPLEMENTED"

    # /api/report/123
    res = client.get("/api/report/test-report-id")
    assert res.status_code == 501
    assert res.json()["error"]["code"] == "NOT_IMPLEMENTED"

def test_missing_params_endpoints():
    # snapshot single missing params
    res = client.get("/api/snapshot?url=")
    assert res.status_code == 422 or res.status_code == 400

    # metadata missing params
    res = client.get("/api/metadata?url=apple.com")
    assert res.status_code == 422 or res.status_code == 400

    # compare missing params
    res = client.get("/api/compare?url=apple.com&ts1=19970101")
    assert res.status_code == 422 or res.status_code == 400

def test_snapshots_success(monkeypatch):
    from app.models import SnapshotsResponse, SnapshotItem, YearDensity
    from app.services.cdx_service import CDXService

    async def mock_fetch(url):
        return SnapshotsResponse(
            url=url,
            normalized_url="example.com",
            total_snapshots=1,
            cached=True,
            snapshots=[
                SnapshotItem(
                    timestamp="20000101120000",
                    year=2000,
                    date="2000-01-01 12:00:00",
                    playback_url="https://web.archive.org/web/20000101120000/http://example.com",
                    clean_playback_url="https://web.archive.org/web/20000101120000id_/http://example.com"
                )
            ],
            years=[YearDensity(year=2000, count=1)]
        )

    monkeypatch.setattr(CDXService, "fetch_snapshots", mock_fetch)
    res = client.get("/api/snapshots?url=example.com")
    assert res.status_code == 200
    data = res.json()
    assert data["normalized_url"] == "example.com"
    assert len(data["snapshots"]) == 1
    assert data["years"][0]["year"] == 2000

def test_snapshot_single_endpoint(monkeypatch):
    from app.models import SnapshotItem
    from app.services.cdx_service import CDXService

    async def mock_get_nearest(url, timestamp):
        if "9999" in timestamp:
            return None
        return SnapshotItem(
            timestamp="19990101120000",
            year=1999,
            date="1999-01-01 12:00:00",
            playback_url="https://web.archive.org/web/19990101120000/http://example.com",
            clean_playback_url="https://web.archive.org/web/19990101120000id_/http://example.com"
        )

    monkeypatch.setattr(CDXService, "get_nearest_snapshot", mock_get_nearest)

    # Found
    res = client.get("/api/snapshot?url=example.com&timestamp=19990101")
    assert res.status_code == 200
    assert res.json()["year"] == 1999

    # Not found
    res = client.get("/api/snapshot?url=example.com&timestamp=9999")
    assert res.status_code == 404

def test_metadata_and_compare_endpoints(monkeypatch):
    from app.models import SnapshotMetadata
    from app.services.metadata_service import MetadataService

    async def mock_get_metadata(url, timestamp):
        is_modern = "2020" in timestamp
        return SnapshotMetadata(
            url=url,
            timestamp=timestamp,
            playback_url=f"https://web.archive.org/web/{timestamp}/http://example.com",
            clean_playback_url=f"https://web.archive.org/web/{timestamp}id_/http://example.com",
            html_size_bytes=5000 if is_modern else 1000,
            dom_node_count=100 if is_modern else 20,
            image_count=5 if is_modern else 1,
            external_resource_count=10 if is_modern else 2,
            has_mobile_viewport=is_modern,
            detected_frameworks=["React / Next.js"] if is_modern else ["Table-Based Layout (Classic Web)"]
        )

    monkeypatch.setattr(MetadataService, "get_or_compute_metadata", mock_get_metadata)

    # Test /api/metadata
    res = client.get("/api/metadata?url=example.com&timestamp=19980101120000")
    assert res.status_code == 200
    meta = res.json()
    assert meta["dom_node_count"] == 20
    assert meta["has_mobile_viewport"] is False

    # Test /api/compare
    res = client.get("/api/compare?url=example.com&ts1=19980101120000&ts2=20200101120000")
    assert res.status_code == 200
    compare_data = res.json()
    assert compare_data["url"] == "example.com"
    assert compare_data["diff"]["dom_node_delta"] == 80
    assert compare_data["diff"]["mobile_viewport_transition"] == "Adopted Mobile Viewport (Responsive)"

