# ModaMix product direction

## Product promise

ModaMix helps online fashion shoppers find real clothing alternatives that keep what they love about a reference item and change what they do not. The v1 shopper has a target product or wardrobe direction and needs the right variation.

## v1 workflow

1. Paste a public retail product URL.
2. Attempt best-effort import of retailer facts and product images.
3. Show the imported title and primary product image for confirmation.
4. Describe what to keep, change, and exclude in text.
5. Review editable structured-preference chips.
6. Filter and rank a curated jacket catalog.
7. Review real product images, prices, retailer links, freshness, and match explanations.

If the imported image is incorrect, ModaMix retries extraction once using another available image or retrieval path. If it still cannot obtain an image, it shows an honest error or blank state and offers a transient manual-upload fallback. Upload is not a primary entry point, and v1 has no image circling or annotation.

## Current implementation

The first import foundation is complete. ModaMix now validates direct public retail URLs, safely retrieves retailer pages, extracts supported JSON-LD product data, and returns complete, partial, or failed import outcomes with field-level structured-page provenance. The interface previews the imported title and default primary image, and safely explains an outdated backend response instead of crashing.

The development workflow now has a matching safety net: `make check` runs backend tests, frontend linting, and a production build; browser tests cover the successful preview and outdated-response recovery; pull requests run these checks automatically. Docker Compose starts the reload-enabled API and frontend together.

This is foundation work, not completion of the full shopper flow. The imported default image is visible, but a shopper cannot yet select another image, request the one permitted retry, or use the manual-upload recovery path.

## Catalog and import boundaries

- Initial market: U.S. shoppers and USD-priced products.
- Initial category: jackets.
- Initial condition: new retail products only. Resale, vintage, rental, and marketplace listings are deferred.
- V1 searches only ModaMix's curated seed catalog; it does not run a live web search for each request.
- Start with 8–12 hand-reviewed listings from two or three retailers; expand to 30–50 once the full workflow works.
- Accept direct public retail product URLs only. Category pages, search pages, homepages, referral links, and social-media links produce a clear input error.
- Preserve retailer facts, structured-page facts, AI visual inference, and unknown values as distinct provenance.
- Record retrieval dates and label results with last-checked data; do not claim live price or availability in v1. Out-of-stock products may be shown with their status, but discontinued products are excluded.
- In-stock Candidate Products rank above equally strong out-of-stock matches.

## V1 attribute vocabulary

Only collect data used for ranking or outcomes: color, silhouette/fit, length, collar, closure, material, warmth, logo presence, and price. Fit is a visual garment trait, not a prediction of how a garment fits a particular shopper. All other detail is optional free text.

## Preferences and ranking

AI may turn a text request into structured preferences and infer visual traits from the confirmed reference image. Ranking itself stays deterministic and explainable.

The shopper must describe at least one Preserved Feature, Requested Change, or Exclusion before ModaMix searches. V1 presents up to six ranked Candidate Products rather than an endless result grid.

- Hard filters: category, stated maximum price, and explicit exclusions.
- Weighted signals: preserved-feature similarity, requested-change satisfaction, soft preferences, freshness/availability where known, and penalties for undesirable traits.
- Requested changes outweigh reference similarity when they conflict.
- ModaMix never silently relaxes hard constraints. When no exact result exists, it explains the blocker and offers explicit tradeoffs.
- Budget is evaluated against the currently purchasable sale price when one is available; the original price is displayed as context.
- Each purchasable colorway is a separate Candidate Product when color is known.
- An imported retailer variant or color is shown with the Reference Image and may be corrected before search when retailer data permits it.
- When multiple imported product images are available, ModaMix selects the primary image by default and lets the shopper select another before retrying extraction.
- Match explanations distinguish retailer facts from visual inferences.
- A Candidate Product with unknown evidence for a hard constraint does not qualify as an exact match. This includes unknown logo status for a "no logo" Exclusion and unknown current price for a maximum-price constraint.
- When no exact match exists, ModaMix presents the blocked requirements and specific, one-at-a-time relaxation choices rather than an empty result page.
- "View at retailer" opens the Candidate Product's direct retailer page in a new browser tab. ModaMix has no cart, checkout, or payment flow in v1.
- Equal match scores are ordered by in-stock status, then lower current price, then more recently checked data.

## Evaluation

Create a version-controlled set of 10–15 representative jacket requests with expected top matches. Track hard-constraint pass rate, top-three relevance, explanation accuracy, URL-extraction completeness, and response time.

## Deferred scope

Accounts, saved collections, persistent upload history, live catalog refreshes, whole-outfit recommendations, broad subjective vibe retrieval, vector search, and opaque AI ranking are deferred.

## Likely next commits

1. `feat(reference): confirm and recover the Reference Image` — let the shopper confirm the imported product and variant, choose another returned image, request one retry for an incorrect image, and use transient manual upload only after image recovery fails.
2. `feat(preferences): turn a Search Request into editable preferences` — require at least one thing to preserve, change, or exclude; interpret the jacket vocabulary; and let the shopper correct it before search.
3. `feat(search): rank seed-catalog Candidate Products` — introduce the hand-reviewed U.S./USD jacket catalog and deterministic, provenance-aware matching of up to six results.
4. `feat(results): handle no Exact Match and retailer handoff` — expose blocked hard constraints, offer one explicit relaxation at a time, and open direct retailer pages in a new tab.
5. `test(flow): verify the complete ModaMix shopper flow` — extend browser coverage across the full path and add the representative ranking evaluation set.

Independent hardening work can proceed separately: expose shopper-facing cache freshness while finishing the importer refactor, and broaden referral/affiliate URL blocking beyond the initial denylist.
