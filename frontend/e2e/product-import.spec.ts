import { expect, test } from "@playwright/test";

const productUrl = "https://retailer.example.test/products/oversized-jacket";

test("shows the imported reference product", async ({ page }) => {
  await page.route("**/api/imports", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        status: "complete",
        product: {
          source_url: productUrl,
          title: "Oversized Hooded Jacket",
          images: ["https://images.example.test/oversized-jacket.jpg"],
          price: "129.99",
          currency: "USD",
          provenance: {
            title: "structured_page",
            images: "structured_page",
            price: "structured_page",
            currency: "structured_page",
          },
        },
      }),
    });
  });

  await page.goto("/");
  await page.getByLabel("Retail product URL").fill(productUrl);
  await page.getByRole("button", { name: "Import product" }).click();

  await expect(
    page.getByRole("heading", { name: "Oversized Hooded Jacket" }),
  ).toBeVisible();
  await expect(
    page.getByRole("img", { name: "Oversized Hooded Jacket" }),
  ).toBeVisible();
  await expect(page.getByText("Title source: Retailer page")).toBeVisible();
});

test("explains an outdated import response instead of crashing", async ({ page }) => {
  await page.route("**/api/imports", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({ status: "queued" }),
    });
  });

  await page.goto("/");
  await page.getByLabel("Retail product URL").fill(productUrl);
  await page.getByRole("button", { name: "Import product" }).click();

  await expect(
    page.getByText("ModaMix received an outdated import response. Restart the backend and try again."),
  ).toBeVisible();
  await expect(page.getByLabel("Imported reference product")).not.toBeVisible();
});
