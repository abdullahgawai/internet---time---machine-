# Initial Prompt
## For use with an AI coding assistant (e.g., Claude Code) to scaffold Internet Time Machine

---

You are helping me build **Internet Time Machine**, a web/app project that lets users enter any website URL and travel back in time through its history using the Internet Archive's Wayback Machine. Users get an interactive timeline/slider to browse and compare snapshots by year, see how the site's design/layout/content/complexity changed, and (optionally) get AI-powered analysis comparing old vs. new screenshots, an evolution score, and a visual redesign timeline.

I have attached two supporting documents for full context: `PRD.md` (product requirements) and `Design.md` (technical/system design). Follow them as the source of truth for scope and architecture.

### Tech stack (required)
- **Frontend:** targeting web first
- **Backend:** Python with FastAPI (async)
- **Historical data:** Wayback Machine / CDX API
- **Storage:** SQLite
- **AI analysis (optional, phase 2):** a vision-capable LLM API for screenshot comparison

### What I want you to do first
1. Set up the project structure:
   - `/backend` — FastAPI app, with clear separation for: CDX/snapshot service, metadata/complexity service, diff service, and (stubbed) AI analysis service. Include SQLite setup with the schema described in `Design.md` section 4.
   - `/frontend` — Flutter app skeleton with screens: Home/Search, Timeline, Snapshot Viewer, Compare.
2. Implement the **Phase 1 MVP** only, in this order:
   a. `GET /api/snapshots?url=` — calls the CDX API, normalizes and caches results in SQLite.
   b. Flutter Home screen — URL input + validation, calls the snapshots endpoint.
   c. Timeline UI — horizontal scrollable timeline of years with available snapshots, draggable playhead.
   d. Snapshot Viewer — loads the correct `web.archive.org/web/{timestamp}/{url}` playback URL in a WebView for the selected year.
   e. `GET /api/metadata?url=&timestamp=` — parses archived HTML for basic complexity metrics (size, DOM node count, image count, mobile viewport detection).
   f. Compare screen — side-by-side two-WebView comparison for two selected years, showing the metadata diff.
3. Add basic caching per the strategy in `Design.md` section 7 (TTL for snapshot lists, indefinite cache for computed metadata).
4. Write a short `README.md` explaining how to run the backend (`uvicorn`) and the Flutter app locally.

### Constraints
- Do not implement the AI vision / evolution score features yet — stub the `/api/analyze` and `/api/evolution-score` endpoints with `501 Not Implemented` responses so the architecture is in place for Phase 3.
- Respect Wayback Machine rate limits — add basic request throttling/backoff on the CDX client.
- Handle the "no snapshots found" and "sparse history" edge cases gracefully in both backend responses and Flutter UI states (per `Design.md` section 8).
- Keep the backend provider-agnostic for the future AI step (don't hardcode a specific vision API yet).

### Deliverable for this session
Working Phase 1 MVP: a user can enter a URL, see a timeline of years, pick two years, and view them side-by-side with a basic metadata diff — backed by real Wayback Machine data and SQLite caching.

Ask me clarifying questions only if something in `PRD.md`/`Design.md` is ambiguous for implementation — otherwise proceed and make reasonable engineering decisions consistent with those documents.
