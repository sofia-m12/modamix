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

The initial category is jackets. URL imports are best-effort; unknown product data remains unknown, and image upload is available only as an import-recovery fallback.
