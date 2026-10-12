# ModaMix

ModaMix helps shoppers find real clothing alternatives that retain the valued qualities of a reference product while satisfying requested changes.

## Language

**Reference Product**:
The retail product supplied by a shopper as the starting point for a ModaMix search.
_Avoid_: Source product, original item, input product

**Reference Image**:
The product image confirmed by the shopper as representing the Reference Product.
_Avoid_: Uploaded image, source image, target image

**Reference Variant**:
The color or style version of a Reference Product that ModaMix imports and presents for shopper confirmation.
_Avoid_: Default variant, source color

**Import**:
The best-effort retrieval of a Reference Product's retailer information and product images from its public URL.
_Avoid_: Scrape, fetch

**Direct Product URL**:
A public retailer URL that identifies one purchasable product, rather than a category, search, home, referral, or social-media page.
_Avoid_: Retail URL, product link

**Candidate Product**:
A catalog product evaluated as a possible alternative to a Reference Product.
_Avoid_: Recommendation, result item, alternative listing

**Availability**:
The last recorded retail status of a Candidate Product. In-stock products rank ahead of equally strong out-of-stock products; out-of-stock products may be shown with their status, but discontinued products are not eligible.
_Avoid_: Live stock, inventory guarantee

**Colorway**:
A purchasable color-specific version of a product style. A known Colorway is evaluated as its own Candidate Product.
_Avoid_: Color option, variant

**Search Request**:
A shopper's natural-language statement of at least one trait to preserve, change, or exclude in an alternative product.
_Avoid_: Prompt, query, search text

**Search Preferences**:
The editable structured interpretation of a Search Request used to filter and rank Candidate Products.
_Avoid_: Filters, search criteria

**Exact Match**:
A Candidate Product that satisfies every known Hard Filter. Unknown evidence does not satisfy a Hard Filter.
_Avoid_: Good match, close match

**Relaxation**:
A shopper-authorized change to a Hard Filter after ModaMix finds no Exact Match.
_Avoid_: Automatic broadening, fallback

**Preserved Feature**:
A trait of the Reference Product that the shopper wants a Candidate Product to retain.
_Avoid_: Keep, similarity signal

**Requested Change**:
A trait the shopper explicitly wants a Candidate Product to have instead of the corresponding trait of the Reference Product.
_Avoid_: Modification, preference

**Exclusion**:
A trait that makes a Candidate Product unacceptable to the shopper.
_Avoid_: Negative preference, penalty

**Retailer Handoff**:
The transition from ModaMix to a Candidate Product's direct retailer page. ModaMix does not participate in checkout or payment.
_Avoid_: Purchase flow, checkout

**Product Fact**:
A retailer-provided or structured-page detail about a product, such as its displayed price or material.
_Avoid_: Inference, attribute

**Visual Inference**:
A visual attribute derived from a product image rather than supplied as a Product Fact.
_Avoid_: Product fact, verified detail

**Fit**:
A visual garment trait such as cropped, oversized, or slim. It is not a prediction of how a garment will fit a particular shopper.
_Avoid_: Size recommendation, body fit

**Match Explanation**:
A plain-language statement of the evidence that caused a Candidate Product to be ranked for a Search Request. It distinguishes Product Facts from Visual Inferences.
_Avoid_: Recommendation reason, score summary
