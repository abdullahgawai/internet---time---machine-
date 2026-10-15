# Design Document
## Internet Time Machine — Technical & System Design

**Version:** 1.0
**Companion to:** PRD.md
**Last Updated:** September 15, 2026

---

## 1. Architecture Overview

```
┌─────────────────────┐      HTTPS/JSON       ┌──────────────────────────┐
│   Flutter Client     │ ◄────────────────────► │   FastAPI Backend        │
│  (Web / iOS / Android)│                        │  (Python, async)         │
└─────────────────────┘                         └──────────────────────────┘
                                                          │        │
                                     ┌────────────────────┘        └───────────────────┐
                                     ▼                                                  ▼
                         ┌───────────────────────┐                         ┌───────────────────────┐
                         │  Wayback Machine /     │                         │  SQLite DB             │
                         │  CDX API (external)    │                         │  (cache, metadata,     │
                         └───────────────────────┘                         │   scores, reports)      │
                                     │                                     └───────────────────────┘
                                     ▼
                         ┌───────────────────────┐          ┌───────────────────────┐
                         │ Headless Browser        │ ───────► │ AI Vision API          │
                         │ (Playwright) — v2        │         │ (optional, screenshot   │
                         │ screenshot capture       │         │ comparison + scoring)   │
                         └───────────────────────┘          └───────────────────────┘
```

**Key design principle:** The backend is a thin orchestration + caching layer over the Wayback Machine. It never re-hosts archived content directly (avoids copyright/hosting complexity) — the archived pages themselves are rendered via `web.archive.org` playback URLs inside a WebView/iframe, while our backend supplies *metadata, diffs, and analysis* around them.

---

## 2. Component Breakdown

### 2.1 Flutter Frontend
- **Home/Search Screen** — URL input, validation, recent searches.
- **Timeline Screen** — horizontal scrollable timeline with year markers, density heatmap (more captures = taller/darker marker), draggable playhead/slider.
- **Snapshot Viewer** — WebView widget loading `https://web.archive.org/web/{timestamp}/{url}`.
- **Compare Screen** — two WebViews in split (side-by-side) or overlay (before/after slider handle) mode; metadata panel below/beside.
- **Evolution Report Screen (v2)** — AI-generated summary, evolution score gauge, redesign timeline with markers, share button.
- **State management:** Riverpod or Bloc (recommend Riverpod for simplicity with async data).

### 2.2 Backend (FastAPI)
- **Snapshot Service** — wraps CDX API calls, normalizes/dedupes snapshot lists, applies caching.
- **Metadata Service** — fetches archived HTML, parses with an HTML parser (e.g., BeautifulSoup/lxml) to compute size, DOM complexity, mobile-meta detection, resource counts.
- **Diff Service** — computes structural diff between two snapshots' metadata (size delta, DOM delta, resource delta).
- **AI Analysis Service (v2)** — orchestrates: trigger headless screenshot capture → send image pair + metadata diff to AI vision API → parse structured response (explanation + score contribution) → persist to DB.
- **Evolution Scoring Engine (v2)** — combines visual diff score + structural diff + content-volume delta + count of detected redesign events into a normalized 0–100 score.
- **Cache Layer** — SQLite-backed cache with TTL for CDX responses and computed metadata, keyed by (url, timestamp).

### 2.3 Data Source: Wayback Machine / CDX API
- **CDX API** (`http://web.archive.org/cdx/search/cdx`) — used to list all available captures for a URL (timestamps, status codes, mimetypes).
- **Playback API** (`https://web.archive.org/web/{timestamp}/{url}`) — used for actually rendering the page.
- Respect Wayback Machine rate limits; implement exponential backoff and request throttling.

### 2.4 AI Vision API (Optional, v2)
- Input: two screenshots (before/after) + structural metadata diff as context.
- Output (structured JSON): natural-language change summary, list of detected change categories (layout, color scheme, navigation, content volume, branding), confidence score, suggested score contribution.
- Provider-agnostic interface so it can point at any vision-capable LLM API.

---

## 3. Data Flow

**Basic snapshot lookup (v1):**
1. User submits URL → Flutter sends `GET /api/snapshots?url=...`
2. Backend checks SQLite cache; if stale/missing, calls CDX API, normalizes results, stores in cache.
3. Backend returns list of `{timestamp, year, status, mimetype}` to client.
4. Client renders timeline; user selects a year → client requests nearest snapshot timestamp → loads playback URL in WebView.

**Comparison flow (v1 metadata / v2 AI):**
1. User selects two timestamps → `GET /api/compare?url=...&ts1=...&ts2=...`
2. Backend fetches (or reuses cached) metadata for both snapshots.
3. (v2) If AI analysis requested: backend triggers headless capture of both pages → sends screenshots to AI vision API → stores structured result.
4. Backend returns combined payload: metadata diff + (optional) AI explanation + evolution score.
5. Client renders comparison view + report.

---

## 4. Database Schema (SQLite)

```sql
-- Cached list of snapshots per URL
CREATE TABLE snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    timestamp TEXT NOT NULL,        -- Wayback timestamp format: YYYYMMDDHHMMSS
    status_code INTEGER,
    mimetype TEXT,
    fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(url, timestamp)
);

-- Computed metadata/complexity per snapshot
CREATE TABLE snapshot_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER REFERENCES snapshots(id),
    html_size_bytes INTEGER,
    dom_node_count INTEGER,
    image_count INTEGER,
    external_resource_count INTEGER,
    has_mobile_viewport BOOLEAN,
    detected_frameworks TEXT,       -- JSON array, best-effort signal detection
    computed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- AI-generated comparison results (v2)
CREATE TABLE ai_comparisons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    timestamp_a TEXT NOT NULL,
    timestamp_b TEXT NOT NULL,
    summary_text TEXT,
    change_categories TEXT,         -- JSON array e.g. ["layout","color","navigation"]
    visual_diff_score REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(url, timestamp_a, timestamp_b)
);

-- Overall evolution score per URL (v2)
CREATE TABLE evolution_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,
    score REAL,
    redesign_events TEXT,           -- JSON array of {timestamp, description}
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 5. API Design (FastAPI)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/snapshots?url=` | List all available snapshot years/timestamps for a URL (cached CDX lookup). |
| GET | `/api/snapshot?url=&timestamp=` | Get nearest valid snapshot + basic metadata for a given date. |
| GET | `/api/metadata?url=&timestamp=` | Get/compute complexity metadata for a single snapshot. |
| GET | `/api/compare?url=&ts1=&ts2=` | Get metadata diff between two snapshots (v1: structural only). |
| POST | `/api/analyze` | Trigger AI screenshot comparison for a (url, ts1, ts2) pair (v2). Body: `{url, ts1, ts2}`. |
| GET | `/api/evolution-score?url=` | Get (or trigger computation of) the full evolution score + redesign timeline (v2). |
| GET | `/api/report/{id}` | Fetch a shareable, pre-rendered evolution report (v2). |

All endpoints return JSON; errors follow a consistent shape: `{"error": {"code": "...", "message": "..."}}`.

---

## 6. Evolution Score Formula (v2, initial heuristic)

```
score = clamp(
    0.35 * visual_diff_score        (0-100, from AI vision comparison)
  + 0.25 * structural_delta_score   (0-100, from DOM/size/resource deltas)
  + 0.20 * content_volume_delta     (0-100, normalized change in text/image volume)
  + 0.20 * redesign_event_density   (0-100, based on # of major jumps / # of years archived)
, 0, 100)
```
This is a starting heuristic — should be tuned against a small labeled set of well-known site redesigns (e.g., known Google/Amazon/Apple redesign years) during v2 development.

---

## 7. Caching & Rate-Limit Strategy

- Cache CDX snapshot lists per URL with a TTL (e.g., 7 days) — snapshot history rarely changes for old dates but new captures can appear.
- Cache computed metadata indefinitely per (url, timestamp) since archived content itself doesn't change.
- Cache AI comparison results indefinitely per (url, ts1, ts2) pair — re-running costs money and the inputs are static.
- Implement a request queue/throttle for outbound CDX calls to stay within Internet Archive's fair-use limits; add backoff on 429/503 responses.

---

## 8. Error Handling & Edge Cases

- **No snapshots found:** show a clear empty state ("This site hasn't been archived yet") rather than an error.
- **Sparse history:** if only 1–2 snapshots exist, disable comparison mode or clearly indicate limited data.
- **Broken archived rendering** (missing CSS/JS in old captures): display a note that rendering fidelity depends on the archive, not the app.
- **AI API failure/timeout:** fall back to structural-only comparison; mark AI insights as "unavailable" rather than blocking the whole comparison view.
- **Robots.txt-excluded domains:** Wayback may return empty/blocked results — surface this explicitly.

---

## 9. Security & Privacy Considerations

- No user accounts required for MVP — reduces PII surface area.
- Sanitize/validate all user-submitted URLs before passing to backend calls (prevent SSRF via odd schemes/internal IPs).
- If screenshots are captured server-side (v2), run headless browser in a sandboxed/isolated environment (no access to internal network).
- Do not persist AI API keys or third-party keys in the client; all AI calls proxy through the backend.

---

## 10. Scalability Notes

- SQLite is fine for MVP/single-instance deployment; plan a migration path to Postgres if usage grows (multi-instance, concurrent writes).
- Screenshot capture (v2) is the most resource-intensive step — should run as an async background job/worker queue (e.g., Celery/RQ or FastAPI background tasks) rather than blocking the request.
- Consider a CDN/object storage (e.g., S3-compatible) for storing captured screenshots and generated report images rather than the DB itself.

---

## 11. Testing Strategy

- Unit tests for CDX response parsing/normalization.
- Integration tests against a small fixed set of well-known URLs with long histories (e.g., archive.org itself, a stable Wikipedia page) to validate timeline building.
- Mock the AI vision API in tests to avoid cost and flakiness; validate prompt/response contract separately.
- Manual QA checklist for WebView rendering fidelity across a sample of very old (pre-2005) vs modern snapshots.
