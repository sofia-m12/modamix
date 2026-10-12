"use client";

import { FormEvent, useState } from "react";

type ImportedProduct = {
  source_url: string;
  title?: string;
  images?: string[];
  price?: string;
  currency?: string;
  provenance?: Record<string, "structured_page">;
};

type ImportResponse = {
  status: "complete" | "partial" | "failed";
  product: ImportedProduct;
};

export function ProductImportForm() {
  const [message, setMessage] = useState("");
  const [preview, setPreview] = useState<ImportResponse | null>(null);
  const [isImporting, setIsImporting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const sourceUrl = formData.get("url");

    setMessage("");
    setPreview(null);
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

      const imported = payload as ImportResponse;
      setPreview(imported);
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

  return (
    <section className="import-panel" aria-labelledby="import-heading">
      <h2 id="import-heading">Start with a product you love</h2>
      <form onSubmit={submit}>
        <label htmlFor="url">Retail product URL</label>
        <input
          id="url"
          name="url"
          type="url"
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
          {preview.product.images?.[0] ? (
            <img src={preview.product.images[0]} alt={preview.product.title ?? "Imported product"} />
          ) : (
            <div className="image-placeholder">No product image available</div>
          )}
          <div>
            <p className="eyebrow">REFERENCE PRODUCT · {preview.status}</p>
            <h3>{preview.product.title ?? "Untitled product"}</h3>
            {preview.product.price && (
              <p>
                {preview.product.currency ?? "USD"} {preview.product.price}
              </p>
            )}
            <a href={preview.product.source_url} target="_blank" rel="noreferrer">
              View source product
            </a>
            <p className="provenance">
              {preview.product.provenance
                ? "Preview details came from structured product metadata."
                : "Some product details could not be imported."}
            </p>
          </div>
        </article>
      )}
    </section>
  );
}
