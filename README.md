# ModaMix

> Keep what you love. Find what you'd change.

ModaMix is a fashion search web app that finds similar clothing based on product images and the changes you want.

## MVP flow

1. Paste a direct retail product URL.
2. Confirm the imported Reference Product and Reference Image.
3. Describe what to keep, change, or exclude.
4. Browse ranked, real-product alternatives with match explanations.

## Repository layout

- `frontend/` — Next.js interface.
- `backend/` — FastAPI service.
- `data/` — Curated seed catalog.
- `docs/` — Engineering documentation.
- `scripts/` — Local catalog utilities.

## Local development

### Install dependencies

Install dependencies once per checkout. Reinstall them only when `backend/pyproject.toml`, `frontend/package.json`, or `frontend/package-lock.json` changes.

Backend first-time setup:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

To refresh backend dependencies later, activation is not required:

```bash
cd backend
.venv/bin/python -m pip install -e '.[dev]'
```

Frontend setup or refresh:

```bash
cd frontend
npm install
```

### Start services

Backend: `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload`

Frontend: `cd frontend && npm run dev`

Or start both reload-enabled services together with Docker Compose. First start OrbStack's Docker engine by opening OrbStack or running `orb start`, then confirm it is ready with `docker info` and run `docker compose up --build`. Open the app at [localhost:3000](http://localhost:3000); the API health endpoint is at [localhost:8000/health](http://localhost:8000/health).

For the usual local workflow, start the app with Docker Compose and run `make check` before opening a pull request.

## Verify your work

Run `make check` after installing the backend virtual environment and frontend dependencies. It runs the backend test suite, frontend linting, and a production frontend build. Run `make test-e2e` after installing the Playwright Chromium browser with `cd frontend && npx playwright install chromium`.

For repeatable manual import checks, use and update [the URL test-case registry](docs/test-urls.md).

The initial category is jackets. URL imports are best-effort; unknown product data remains unknown, and image upload is available only as an import-recovery fallback.
