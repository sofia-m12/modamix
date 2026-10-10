"""Future catalog ingestion entrypoint for ModaMix."""
from pathlib import Path
def main() -> None:
    catalog = Path(__file__).parents[1] / "data" / "seed-products.json"
    print(f"Catalog source: {catalog}")
if __name__ == "__main__":
    main()
