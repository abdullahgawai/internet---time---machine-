# 🕰️ Internet Time Machine — Digital Archaeology & History Explorer

An interactive web archaeology platform that visualizes the evolution of websites across decades using historical data from the Wayback Machine. Features interactive timeline scrubbing, side-by-side era comparisons, DOM complexity analysis, and local SQLite caching.

---

## ✨ Features

- **Decade Scrubber & Density Bar**: Navigate historical snapshots from the 1990s through present day with capture density indicators.
- **Side-by-Side Comparison**: Compare any two eras of a website simultaneously with synchronized scrolling and structural diff drawers.
- **Structural Complexity Analysis**: Analyze DOM node counts, HTML payload sizes, image asset counts, and mobile viewport responsiveness over time.
- **Technology Signal Detection**: Best-effort heuristic identification of frameworks and architectures (Table layouts, Flash, jQuery, Bootstrap, React, HTML5 semantic layout).
- **SQLite Caching & Instant Seeding**: Fast local caching with TTL and pre-seeded datasets for iconic web milestones (`apple.com`, `google.com`, `amazon.com`, `spacejam.com`, `yahoo.com`, `wikipedia.org`).

---

## 🛠️ Tech Stack

- **Backend**: Python 3, FastAPI, Uvicorn, SQLite (`aiosqlite`), HTTPX, BeautifulSoup4
- **Frontend**: Vanilla HTML5, CSS3, JavaScript (ES Modules), Vite

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Node.js 18+

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Start backend server
python run.py
```
Backend runs at `http://127.0.0.1:8000`.

### 3. Seed Local Data (Optional but Recommended)
Populate the SQLite cache with 480+ historical snapshots across iconic websites:
```bash
python seed_data.py
```

### 4. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
Frontend runs at `http://localhost:5173`.

---

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── routes/        # API endpoints (snapshots, metadata, compare)
│   │   ├── services/      # CDX service, metadata analysis, diffing
│   │   ├── database.py    # SQLite schema and async connections
│   │   ├── models.py      # Pydantic data schemas
│   │   └── main.py        # FastAPI app initialization
│   ├── requirements.txt
│   └── run.py             # Backend entry point
├── frontend/
│   ├── src/
│   │   ├── styles/        # CSS design system, glassmorphism, responsive styles
│   │   ├── api.js         # Backend API client
│   │   └── app.js         # Interactive timeline & comparison controller
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── seed_data.py           # Database seeder for instant offline exploration
├── .gitignore
└── README.md
```
