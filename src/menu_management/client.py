"""HTTP client for querying the product-management service."""

from typing import Any

import httpx


class ProductClient:
    """Client for retrieving product details via GET /products/{product_id}."""

    def __init__(
        self,
        base_url: str = "http://product-management",
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._client = httpx.Client(base_url=base_url, transport=transport)

    def get_product(self, product_id: str) -> dict[str, Any] | None:
        """Fetch a product by ID. Returns None when the product is not found (404)."""
        response = self._client.get(f"/products/{product_id}")
        if response.status_code == httpx.codes.NOT_FOUND:
            return None
        response.raise_for_status()
        return response.json()

    def list_products(self) -> list[dict[str, Any]]:
        """Fetch all products from product-management."""
        response = self._client.get("/products")
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()
