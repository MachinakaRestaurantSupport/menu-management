"""FastAPI application for menu management."""

from fastapi import FastAPI, HTTPException, status

from menu_management.client import ProductClient
from menu_management.models import Channel, Menu, MenuCreate, MenuPublishUpdate
from menu_management.store import MenuStore


def create_app(product_client: ProductClient | None = None) -> FastAPI:
    """Create and configure the menu-management FastAPI application."""
    app = FastAPI(title="menu-management", version="0.1.0")
    store = MenuStore()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "menu-management"}

    @app.post("/menus", response_model=Menu, status_code=status.HTTP_201_CREATED)
    def create_menu(payload: MenuCreate) -> Menu:
        if product_client is not None:
            for category in payload.categories:
                for product_id in category.product_ids:
                    product = product_client.get_product(product_id)
                    if product is None:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product not found: {product_id}",
                        )
                    if payload.channel == "takeout" and not product.get("takeout_available", False):
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"Product is not available for takeout: {product_id}",
                        )
        return store.create(payload)

    @app.get("/menus/{channel}", response_model=list[Menu])
    def list_published_menus(channel: Channel) -> list[Menu]:
        return store.list_published(channel)

    @app.patch("/menus/{menu_id}/publish", response_model=Menu)
    def update_menu_publish(menu_id: str, payload: MenuPublishUpdate) -> Menu:
        updated = store.set_published(menu_id, payload.published)
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Menu not found: {menu_id}",
            )
        return updated

    return app


app = create_app()
