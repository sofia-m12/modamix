.PHONY: check test-backend lint-frontend build-frontend test-e2e

check: test-backend lint-frontend build-frontend

test-backend:
	cd backend && .venv/bin/python -m pytest -q

lint-frontend:
	cd frontend && npm run lint

build-frontend:
	cd frontend && npm run build

test-e2e:
	cd frontend && npm run test:e2e
