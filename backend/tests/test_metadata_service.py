import pytest
from app.services.metadata_service import MetadataService
from app.services.diff_service import DiffService
from app.models import SnapshotMetadata

SAMPLE_90S_HTML = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<html>
<head><title>Retro Site 1998</title></head>
<body bgcolor="#FFFFFF">
  <table border="1" cellpadding="5">
    <tr>
      <td><img src="/images/logo.gif" width="100" height="50"></td>
      <td><h1>Welcome to our homepage!</h1></td>
    </tr>
  </table>
  <table border="0" cellpadding="2">
    <tr><td><a href="/news.html">News</a></td></tr>
  </table>
  <table border="0">
    <tr><td>Footer copyright 1998</td></tr>
  </table>
  <embed src="/sound.mid" autostart="true">
</body>
</html>
"""

SAMPLE_MODERN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Modern App 2024</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5/dist/css/bootstrap.min.css">
  <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
</head>
<body>
  <header><nav class="navbar navbar-expand-lg">Brand</nav></header>
  <main class="container">
    <div data-reactroot="">
      <img src="hero.webp" alt="Hero">
      <img src="thumb.webp" alt="Thumb">
      <svg><circle cx="50" cy="50" r="40"/></svg>
    </div>
  </main>
  <footer>Footer content</footer>
</body>
</html>
"""

def test_extract_metrics_90s():
    metrics = MetadataService.extract_metrics_from_html(SAMPLE_90S_HTML, len(SAMPLE_90S_HTML))
    assert metrics["dom_node_count"] > 10
    assert metrics["image_count"] == 1
    assert metrics["has_mobile_viewport"] is False
    assert "Table-Based Layout (Classic Web)" in metrics["detected_frameworks"]
    assert "Adobe Flash" in metrics["detected_frameworks"]

def test_extract_metrics_modern():
    metrics = MetadataService.extract_metrics_from_html(SAMPLE_MODERN_HTML, len(SAMPLE_MODERN_HTML))
    assert metrics["has_mobile_viewport"] is True
    assert metrics["image_count"] == 3 # 2 img + 1 svg
    assert "Bootstrap" in metrics["detected_frameworks"]
    assert "jQuery" in metrics["detected_frameworks"]
    assert "React / Next.js" in metrics["detected_frameworks"]
    assert "HTML5 Semantic Layout" in metrics["detected_frameworks"]

def test_diff_service():
    snap_a = SnapshotMetadata(
        url="example.com",
        timestamp="19980101120000",
        playback_url="https://web.archive.org/web/19980101120000/http://example.com",
        clean_playback_url="https://web.archive.org/web/19980101120000id_/http://example.com",
        html_size_bytes=1000,
        dom_node_count=20,
        image_count=1,
        external_resource_count=1,
        has_mobile_viewport=False,
        detected_frameworks=["Table-Based Layout (Classic Web)"]
    )
    snap_b = SnapshotMetadata(
        url="example.com",
        timestamp="20240101120000",
        playback_url="https://web.archive.org/web/20240101120000/http://example.com",
        clean_playback_url="https://web.archive.org/web/20240101120000id_/http://example.com",
        html_size_bytes=5000,
        dom_node_count=80,
        image_count=5,
        external_resource_count=8,
        has_mobile_viewport=True,
        detected_frameworks=["React / Next.js", "HTML5 Semantic Layout"]
    )

    diff = DiffService.compute_diff(snap_a, snap_b)
    assert diff.html_size_delta == 4000
    assert diff.html_size_change_pct == 400.0
    assert diff.dom_node_delta == 60
    assert diff.image_count_delta == 4
    assert diff.external_resource_delta == 7
    assert diff.mobile_viewport_transition == "Adopted Mobile Viewport (Responsive)"
    assert "React / Next.js" in diff.frameworks_added
    assert "Table-Based Layout (Classic Web)" in diff.frameworks_removed
