"use client";

import { FormEvent, useState } from "react";

type ImportedProduct = {
  source_url: string;
  title?: string;
  images?: string[];
  price?: string;
  currency?: string;
  provenance?: Record<string, "structured_page" | "visual_inference">;
};

type ImportResponse = {
  status: "complete" | "partial" | "failed";
  product: ImportedProduct;
};

type ConfirmedReferenceProduct = {
  sourceUrl: string;
  title: string;
  variant: string;
  image: string;
};

function provenanceLabel(
  field: string,
  provenance: ImportedProduct["provenance"],
) {
  const source = provenance?.[field];
  if (source === "structured_page") {
    return "Retailer page";
  }
  if (source === "visual_inference") {
    return "Image analysis";
  }
  return "Unknown";
}

function isImportResponse(value: unknown): value is ImportResponse {
  if (typeof value !== "object" || value === null) {
    return false;
  }

  const response = value as Partial<ImportResponse>;
  return (
    (response.status === "complete" || response.status === "partial" || response.status === "failed") &&
    typeof response.product === "object" &&
    response.product !== null &&
    typeof response.product.source_url === "string"
  );
}

export function ProductImportForm() {
  const [sourceUrl, setSourceUrl] = useState("");
  const [message, setMessage] = useState("");
  const [preview, setPreview] = useState<ImportResponse | null>(null);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [referenceTitle, setReferenceTitle] = useState("");
  const [referenceVariant, setReferenceVariant] = useState("");
  const [confirmedReferenceProduct, setConfirmedReferenceProduct] =
    useState<ConfirmedReferenceProduct | null>(null);
  const [isImporting, setIsImporting] = useState(false);

  function startOver() {
    setSourceUrl("");
    setMessage("");
    setPreview(null);
    setSelectedImage(null);
    setReferenceTitle("");
    setReferenceVariant("");
    setConfirmedReferenceProduct(null);
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setMessage("");
    setPreview(null);
    setSelectedImage(null);
    setReferenceTitle("");
    setReferenceVariant("");
    setConfirmedReferenceProduct(null);
    setIsImporting(true);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/imports`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ source_url: sourceUrl }),
        },
      );
      const payload = await response.json();

      if (!response.ok) {
        setMessage(
          typeof payload.detail === "string"
            ? payload.detail
            : "ModaMix could not import that product URL.",
        );
        return;
      }

      if (!isImportResponse(payload)) {
        setMessage("ModaMix received an outdated import response. Restart the backend and try again.");
        return;
      }

      const imported = payload;
      setPreview(imported);
      setSelectedImage(imported.product.images?.[0] ?? null);
      setReferenceTitle(imported.product.title ?? "");
      setMessage(
        imported.status === "failed"
          ? "ModaMix could not find a usable product preview at that URL."
          : "Review the imported Reference Product before continuing.",
      );
    } catch {
      setMessage("ModaMix could not reach the import service. Please try again.");
    } finally {
      setIsImporting(false);
    }
  }

  function confirmReferenceProduct() {
    if (selectedImage === null || referenceTitle.trim() === "" || preview === null) {
      return;
    }

    setConfirmedReferenceProduct({
      sourceUrl: preview.product.source_url,
      title: referenceTitle.trim(),
      variant: referenceVariant.trim(),
      image: selectedImage,
    });
    setMessage("");
  }

  if (confirmedReferenceProduct) {
    return (
      <section className="import-panel" aria-labelledby="import-heading">
        <h2 id="import-heading">Reference Product confirmed</h2>
        <article className="product-preview" aria-label="Confirmed reference product">
          <img src={confirmedReferenceProduct.image} alt={confirmedReferenceProduct.title} />
          <div>
            <p className="eyebrow">REFERENCE PRODUCT</p>
            <h3>{confirmedReferenceProduct.title}</h3>
            {confirmedReferenceProduct.variant && <p>{confirmedReferenceProduct.variant}</p>}
            <p className="provenance">Confirmed by you</p>
            <a href={confirmedReferenceProduct.sourceUrl} target="_blank" rel="noreferrer">
              View source product
            </a>
          </div>
        </article>
        <p>Your Reference Product is ready for the next step.</p>
        <button type="button" onClick={startOver}>
          Try another product URL
        </button>
      </section>
    );
  }

  const imageOptions = preview?.product.images?.slice(0, 4) ?? [];
  const titleWasCorrected = preview !== null && referenceTitle !== (preview.product.title ?? "");

  return (
    <section className="import-panel" aria-labelledby="import-heading">
      <h2 id="import-heading">Start with a product you love</h2>
      <form onSubmit={submit}>
        <label htmlFor="url">Retail product URL</label>
        <input
          id="url"
          name="url"
          type="url"
          value={sourceUrl}
          onChange={(event) => setSourceUrl(event.target.value)}
          placeholder="https://retailer.com/products/jacket"
          required
        />
        <button type="submit" disabled={isImporting}>
          {isImporting ? "Importing…" : "Import product"}
        </button>
      </form>
      {message && <p aria-live="polite">{message}</p>}
      {preview?.status !== "failed" && preview && (
        <article className="product-preview" aria-label="Imported reference product">
          {selectedImage ? (
            <img src={selectedImage} alt={referenceTitle || "Imported product"} />
          ) : (
            <div className="image-placeholder">No product image available</div>
          )}
          <div>
            <p className="eyebrow">REFERENCE PRODUCT · {preview.status}</p>
            <label htmlFor="reference-title">Reference product title</label>
            <input
              id="reference-title"
              value={referenceTitle}
              onChange={(event) => setReferenceTitle(event.target.value)}
              required
            />
            {titleWasCorrected && <p className="provenance">Title corrected by you</p>}
            <label htmlFor="reference-variant">Color or variant</label>
            <input
              id="reference-variant"
              value={referenceVariant}
              onChange={(event) => setReferenceVariant(event.target.value)}
              placeholder="Optional"
            />
            {referenceVariant && <p className="provenance">Variant provided by you</p>}
            <p className="provenance">
              Title source: {provenanceLabel("title", preview.product.provenance)} · Image source:{" "}
              {provenanceLabel("images", preview.product.provenance)}
            </p>
            {preview.product.price && (
              <p>
                {preview.product.currency ? `${preview.product.currency} ` : ""}
                {preview.product.price}
              </p>
            )}
            <p className="provenance">
              Price source: {provenanceLabel("price", preview.product.provenance)} · Currency source:{" "}
              {provenanceLabel("currency", preview.product.provenance)}
            </p>
            <a href={preview.product.source_url} target="_blank" rel="noreferrer">
              View source product
            </a>
          </div>
          {imageOptions.length > 0 && (
            <fieldset className="image-options">
              <legend>Choose the Reference Image</legend>
              {imageOptions.map((image, index) => (
                <button
                  key={image}
                  type="button"
                  className={selectedImage === image ? "image-option is-selected" : "image-option"}
                  aria-label={`Select image ${index + 1}`}
                  aria-pressed={selectedImage === image}
                  onClick={() => setSelectedImage(image)}
                >
                  <img src={image} alt={`Image option ${index + 1}`} />
                </button>
              ))}
            </fieldset>
          )}
          <div className="reference-actions">
            <button
              type="button"
              onClick={confirmReferenceProduct}
              disabled={selectedImage === null || referenceTitle.trim() === ""}
            >
              Confirm Reference Product
            </button>
            <button type="button" onClick={startOver}>
              Try another product URL
            </button>
          </div>
        </article>
      )}
    </section>
  );
}
