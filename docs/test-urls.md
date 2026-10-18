# URL import test cases

Use this list for repeatable manual checks of the direct-product URL import flow. Record the outcome against the current local backend; retailer pages can change over time, so a prior result is not a guarantee of a future result.

| Retailer | Product URL | Last observed outcome | Notes |
| --- | --- | --- | --- |
| Mango | https://shop.mango.com/us/en/p/women/jackets/bombers/oversized-hooded-jacket/27083340/76/00 | Import may fail or be partial | Useful unsupported/limited-extraction case. |
| Gap | https://www.gap.com/browse/product.do?pid=455069002&vid=1#pdp-page-content | Imported successfully during initial URL-import testing | Useful complete-import baseline. |

## How to add a case

Add direct public retailer product pages only. Record whether the result was complete, partial, failed, or rejected, and briefly note why when known. Do not add affiliate, referral, social-media, category, search, or private URLs as success cases; add them to API tests when they are intended validation coverage.
