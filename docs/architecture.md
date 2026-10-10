# ModaMix architecture

The web client calls the FastAPI service for URL import and product search. The backend keeps retailer facts, AI-inferred visual attributes, and unknown fields separate. The MVP ranks a curated jacket catalog with deterministic category, budget, desired-feature, and exclusion rules.

External credentials remain backend-only. URL retrieval must validate destinations, reject private or internal addresses, use explicit timeouts, and cache completed imports.
