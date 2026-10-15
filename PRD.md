# Product Requirements Document (PRD)
## Internet Time Machine

**Version:** 1.0
**Status:** Draft
**Owner:** [Your Name]
**Last Updated:** September 15, 2026

---

## 1. Executive Summary

Internet Time Machine is a web app that lets users enter any website URL and travel through its history using archived snapshots from the Wayback Machine. Beyond simple browsing of old pages, the product acts as a "digital archaeology" tool: it visualizes how a site's design, layout, content, complexity, and features evolved over time, and — optionally — uses AI vision analysis to explain major redesigns and generate an "evolution score" for the site.

---

## 2. Problem Statement

The web changes constantly, but most users have no easy way to see *how* a site evolved beyond manually digging through the Wayback Machine's clunky calendar UI. There is no tool that:
- Lets you compare two points in a site's history side-by-side.
- Summarizes what actually changed (design, content, tech) in plain language.
- Quantifies a site's evolution in a simple, shareable way.

This is valuable for designers researching visual trends, developers studying legacy tech stacks, historians/journalists documenting internet culture, and curious everyday users who want nostalgic trips through old websites (Amazon 1999, Google 2000, etc.).

---

## 3. Goals & Objectives

| Goal | Description |
|---|---|
| G1 | Let a user retrieve and browse historical snapshots of any URL by year/date. |
| G2 | Provide an interactive timeline/slider for quick navigation across years. |
| G3 | Support side-by-side ("then vs. now") comparison of two snapshots. |
| G4 | Surface structural/technical metadata about each snapshot (page size, tech signals, mobile-friendliness, etc.). |
| G5 | (Optional/Phase 2) Use AI vision to compare screenshots, explain changes, and produce an evolution score. |
| G6 | Make the experience fast, visually engaging, and shareable. |

### Non-Goals (v1)
- Not a general-purpose web archive replacement (we depend on the Wayback Machine as the data source, not our own crawler).
- Not aiming to archive *new* snapshots ourselves in v1 (read-only against existing archives).
- Not building a full CMS or user-generated-content platform.

---

## 4. Target Users

1. **Designers & UX researchers** — studying visual design trends over decades.
2. **Developers/Tech historians** — curious about legacy frameworks, load times, mobile transitions.
3. **Journalists & content creators** — need quick "then vs now" visuals for articles/social posts.
4. **Casual/nostalgic users** — want to relive old internet (early Google, MySpace, Amazon, etc.).
5. **Students/educators** — teaching internet history or web design evolution.

---

## 5. User Stories

- As a user, I want to type in a URL and see a timeline of all the years snapshots exist, so I can pick a period to explore.
- As a user, I want to drag a slider between two years and see the page transform, so I can visually compare eras.
- As a user, I want to view two snapshots side-by-side (split screen), so I can spot differences directly.
- As a user, I want a summary of what changed between two snapshots (layout, colors, navigation, content volume), so I don't have to spot differences manually.
- As a user, I want an "evolution score" for a site, so I have a quick, shareable metric of how much it has changed.
- As a user, I want to see a visual timeline highlighting "major redesign" moments, so I can jump straight to the interesting jumps instead of scrubbing year by year.
- As a user, I want to export or share a comparison (image/link), so I can post it on social media or embed it in an article.
- As a user, I want the app to work reasonably well even when a site has very few captured snapshots.

---

## 6. Core Features (v1 — MVP)

1. **URL Input & Validation**
   - Accept any domain/URL; normalize and validate.
   - Query the Wayback Machine CDX API for the full list of available snapshots.

2. **Timeline / Year Slider**
   - Interactive horizontal timeline showing years with available snapshots (density indicator for how many captures exist per year).
   - Selecting a year/date loads the closest available snapshot.

3. **Snapshot Viewer**
   - Render the archived page (via Wayback Machine's own playback URL, e.g. `web.archive.org/web/{timestamp}/{url}`) inside an embedded viewer.

4. **Side-by-Side Comparison**
   - Pick two dates → split-screen or slider ("before/after") view of both snapshots.
   - Synchronized scrolling (best-effort, since archived pages are iframed).

5. **Basic Metadata Analysis**
   - Page size (approx. HTML byte size), number of images, presence of CSS/JS, mobile viewport meta tag detection, HTTP status of the capture.
   - Simple "complexity" heuristics (DOM node count, external resource count) computed by parsing the archived HTML.

6. **Snapshot Caching**
   - Cache fetched snapshot lists and metadata locally (SQLite) to avoid hammering the CDX API and to speed up repeat lookups.

---

## 7. Advanced / Optional Features (v2 — AI-Enhanced)

1. **AI Screenshot Comparison**
   - Capture rendered screenshots of two snapshots (headless browser) and send both to an AI vision model.
   - AI returns a natural-language explanation of major visual/layout/content changes.

2. **Evolution Score**
   - A composite score (0–100) derived from: visual difference (screenshot diffing), structural complexity delta, content volume delta, and number of major redesign events detected across the site's full history.

3. **Redesign Timeline / "Major Moments"**
   - Automatically scan snapshots across years, detect large visual/structural jumps, and mark them as "redesign events" on the timeline (e.g., "2011: Major redesign — new logo, grid layout introduced").

4. **Design Trend Tagging**
   - Optionally tag each era with recognizable design trends (e.g., "skeuomorphism," "flat design," "dark mode era") using AI classification.

5. **Shareable Reports**
   - Auto-generate a shareable "Evolution Report" (image or link) summarizing a site's journey, timeline highlights, and score.

---

## 8. Success Metrics

- **Activation:** % of new users who successfully load a snapshot within their first session.
- **Engagement:** Average number of snapshots/years viewed per session.
- **Retention:** % of users returning to compare a different site within 7 days.
- **AI feature adoption:** % of sessions that trigger AI comparison (v2).
- **Performance:** Median time from URL submission to first snapshot render (< 3s target for cached, < 8s for cold lookups).
- **Reliability:** Successful snapshot resolution rate (snapshots found & rendered without error) > 90%.

---

## 9. Constraints & Assumptions

- Fully dependent on the Wayback Machine's availability, rate limits, and archive completeness — some sites/eras will have sparse or no data.
- Wayback Machine snapshots may render with broken assets, ads, or partial resources; the app must handle degraded rendering gracefully.
- AI vision analysis is optional and gated behind an API cost — must design for graceful fallback if AI is disabled or a call fails.
- No guarantee of exact synchronized scroll/interaction between two differently-structured archived pages.

---

## 10. Tech Stack (Reference)

| Layer | Technology |
|---|---|
| Frontend | Flutter (web + mobile) |
| Backend | Python (FastAPI preferred over Flask for async + auto docs) |
| Historical Data Source | Wayback Machine / CDX API |
| Storage | SQLite (metadata, cache, evolution scores) |
| AI Analysis (optional) | Vision-capable LLM API (e.g., Claude/GPT-4V-class model) |
| Screenshot Capture | Headless browser (Playwright/Puppeteer) for v2 AI features |

---

## 11. Phased Roadmap

**Phase 1 — MVP (Core Time Travel)**
- URL input, CDX snapshot lookup, timeline UI, single snapshot viewer, SQLite caching.

**Phase 2 — Comparison Tools**
- Side-by-side/slider comparison, basic metadata analysis (size, complexity, mobile-friendliness).

**Phase 3 — AI Intelligence Layer**
- Screenshot capture pipeline, AI-powered change explanations, evolution score, redesign timeline detection.

**Phase 4 — Polish & Sharing**
- Shareable evolution reports, design trend tagging, performance optimization, expanded platform support.

---

## 12. Open Questions

- Do we self-host screenshot capture (cost/infra) or rely on a third-party screenshot API?
- What's the acceptable cost ceiling per AI analysis call, and do we rate-limit/cache AI results per (url, date-pair)?
- Should we support arbitrary paths (e.g., `/blog/post-1`) or focus v1 on homepages only?
- How do we handle sites blocked from archiving (robots.txt exclusions) — show a clear "not archived" state.
