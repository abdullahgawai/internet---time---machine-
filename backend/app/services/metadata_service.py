import json
import logging
from typing import Optional, List
import httpx
from bs4 import BeautifulSoup

from app.database import get_db
from app.models import SnapshotMetadata
from app.services.cdx_service import normalize_url, USER_AGENT, WAYBACK_PLAYBACK_BASE

logger = logging.getLogger(__name__)

class MetadataService:
    @staticmethod
    def extract_metrics_from_html(html_content: str, html_size_bytes: int) -> dict:
        """Parse HTML and compute complexity metrics and tech signal heuristics."""
        soup = BeautifulSoup(html_content, "html.parser")

        # 1. Total DOM elements
        all_tags = soup.find_all()
        dom_node_count = len(all_tags)

        # 2. Images
        images = soup.find_all(["img", "picture", "svg"])
        image_count = len(images)

        # 3. External resources (stylesheets, scripts, iframes, embeds)
        stylesheets = soup.find_all("link", rel=lambda x: x and "stylesheet" in x)
        scripts = soup.find_all("script", src=True)
        embeds = soup.find_all(["iframe", "embed", "object"])
        external_resource_count = len(stylesheets) + len(scripts) + len(embeds)

        # 4. Mobile viewport tag detection
        has_mobile_viewport = False
        viewport_tag = soup.find("meta", attrs={"name": lambda x: x and x.lower() == "viewport"})
        if viewport_tag and viewport_tag.get("content"):
            has_mobile_viewport = True

        # 5. Detected frameworks / legacy signals heuristics
        frameworks: List[str] = []
        lower_html = html_content.lower()

        # Table-based layout check (typical 90s/early 2000s web)
        tables = soup.find_all("table")
        if len(tables) >= 3 or any(t.get("border") or t.get("cellpadding") for t in tables):
            frameworks.append("Table-Based Layout (Classic Web)")

        # Flash embed detection
        if soup.find_all(["embed", "object"]) or ".swf" in lower_html:
            frameworks.append("Adobe Flash")

        # jQuery
        if "jquery" in lower_html or soup.find("script", src=lambda s: s and "jquery" in s.lower()):
            frameworks.append("jQuery")

        # Bootstrap
        if "bootstrap" in lower_html or soup.find("link", href=lambda h: h and "bootstrap" in h.lower()):
            frameworks.append("Bootstrap")

        # WordPress
        if "wp-content" in lower_html or "wp-includes" in lower_html:
            frameworks.append("WordPress")

        # React / Next.js
        if "react" in lower_html or "__next" in lower_html or soup.find(attrs={"data-reactroot": True}):
            frameworks.append("React / Next.js")

        # Vue.js / Nuxt
        if "__nuxt" in lower_html or any("data-v-" in tag.attrs for tag in all_tags):
            frameworks.append("Vue.js")

        # Font Awesome / Web Fonts
        if "font-awesome" in lower_html or "fonts.googleapis.com" in lower_html:
            frameworks.append("Web Fonts / FontAwesome")

        # Semantic HTML5 (header, nav, article, footer, section)
        html5_tags = soup.find_all(["header", "nav", "article", "section", "main", "footer"])
        if len(html5_tags) >= 2:
            frameworks.append("HTML5 Semantic Layout")

        return {
            "dom_node_count": dom_node_count,
            "image_count": image_count,
            "external_resource_count": external_resource_count,
            "has_mobile_viewport": has_mobile_viewport,
            "detected_frameworks": frameworks
        }

    @classmethod
    async def get_or_compute_metadata(cls, raw_url: str, timestamp: str) -> SnapshotMetadata:
        """
        Fetch or compute structural metadata for (url, timestamp).
        Checks indefinite SQLite cache first.
        """
        norm_url = normalize_url(raw_url)
        clean_playback_url = f"{WAYBACK_PLAYBACK_BASE}/{timestamp}id_/http://{norm_url}"
        playback_url = f"{WAYBACK_PLAYBACK_BASE}/{timestamp}/http://{norm_url}"

        # 1. Check SQLite cache
        async with get_db() as db:
            cursor = await db.execute(
                """SELECT html_size_bytes, dom_node_count, image_count, 
                          external_resource_count, has_mobile_viewport, 
                          detected_frameworks, computed_at
                   FROM snapshot_metadata
                   WHERE url = ? AND timestamp = ?""",
                (norm_url, timestamp)
            )
            row = await cursor.fetchone()
            if row:
                frameworks = json.loads(row["detected_frameworks"]) if row["detected_frameworks"] else []
                return SnapshotMetadata(
                    url=raw_url,
                    timestamp=timestamp,
                    playback_url=playback_url,
                    clean_playback_url=clean_playback_url,
                    html_size_bytes=row["html_size_bytes"],
                    dom_node_count=row["dom_node_count"],
                    image_count=row["image_count"],
                    external_resource_count=row["external_resource_count"],
                    has_mobile_viewport=bool(row["has_mobile_viewport"]),
                    detected_frameworks=frameworks,
                    computed_at=row["computed_at"]
                )

        # 2. Fetch archived HTML from Wayback playback URL
        html_size_bytes = 0
        metrics = {
            "dom_node_count": 0,
            "image_count": 0,
            "external_resource_count": 0,
            "has_mobile_viewport": False,
            "detected_frameworks": []
        }

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                res = await client.get(
                    clean_playback_url,
                    headers={"User-Agent": USER_AGENT}
                )
                if res.status_code == 200:
                    html_content = res.text
                    html_size_bytes = len(res.content)
                    metrics = cls.extract_metrics_from_html(html_content, html_size_bytes)
                else:
                    logger.warning("Could not fetch playback HTML (%s): status %s", clean_playback_url, res.status_code)
        except Exception as exc:
            logger.warning("Error fetching playback HTML for %s: %s", clean_playback_url, exc)

        # 3. Store in SQLite cache indefinitely
        async with get_db() as db:
            await db.execute(
                """INSERT OR REPLACE INTO snapshot_metadata (
                       url, timestamp, html_size_bytes, dom_node_count,
                       image_count, external_resource_count, has_mobile_viewport,
                       detected_frameworks
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    norm_url,
                    timestamp,
                    html_size_bytes,
                    metrics["dom_node_count"],
                    metrics["image_count"],
                    metrics["external_resource_count"],
                    metrics["has_mobile_viewport"],
                    json.dumps(metrics["detected_frameworks"])
                )
            )
            await db.commit()

        return SnapshotMetadata(
            url=raw_url,
            timestamp=timestamp,
            playback_url=playback_url,
            clean_playback_url=clean_playback_url,
            html_size_bytes=html_size_bytes,
            dom_node_count=metrics["dom_node_count"],
            image_count=metrics["image_count"],
            external_resource_count=metrics["external_resource_count"],
            has_mobile_viewport=metrics["has_mobile_viewport"],
            detected_frameworks=metrics["detected_frameworks"],
            computed_at=None
        )
