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

Backend: `cd backend && python -m venv .venv && source .venv/bin/activate && pip install -e '.[dev]' && uvicorn app.main:app --reload`

Frontend: `cd frontend && npm install && npm run dev`

Or start both reload-enabled services together with `docker compose up --build`. Open the app at [localhost:3000](http://localhost:3000); the API health endpoint is at [localhost:8000/health](http://localhost:8000/health).

For the usual local workflow, start the app with Docker Compose and run `make check` before opening a pull request.

## Verify your work

Run `make check` after installing the backend virtual environment and frontend dependencies. It runs the backend test suite, frontend linting, and a production frontend build. Run `make test-e2e` after installing the Playwright Chromium browser with `cd frontend && npx playwright install chromium`.

The initial category is jackets. URL imports are best-effort; unknown product data remains unknown, and image upload is available only as an import-recovery fallback.
