"""Unit tests for menu management API."""

import httpx
from fastapi.testclient import TestClient

from menu_management.client import ProductClient
from menu_management.main import create_app

PRODUCTS = {
    "prod-1": {"id": "prod-1", "name": "Karaage Bento", "takeout_available": True},
    "prod-2": {"id": "prod-2", "name": "Draft Beer", "takeout_available": False},
}


def make_product_client() -> ProductClient:
    """Create a ProductClient backed by httpx.MockTransport."""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.startswith("/products/"):
            product_id = request.url.path.removeprefix("/products/")
            product = PRODUCTS.get(product_id)
            if product is None:
                return httpx.Response(404, json={"detail": "Not found"})
            return httpx.Response(200, json=product)
        return httpx.Response(404)

    return ProductClient(
        base_url="http://product-management",
        transport=httpx.MockTransport(handler),
    )


def test_health() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "menu-management"}


def test_create_and_list_menus_by_channel() -> None:
    app = create_app(product_client=make_product_client())
    client = TestClient(app)

    dine_in_res = client.post(
        "/menus",
        json={
            "channel": "dine_in",
            "title": "Dinner Menu",
            "categories": [{"name": "Drinks", "product_ids": ["prod-2"]}],
        },
    )
    assert dine_in_res.status_code == 201
    dine_in_data = dine_in_res.json()
    assert dine_in_data["channel"] == "dine_in"
    assert dine_in_data["title"] == "Dinner Menu"
    assert dine_in_data["published"] is True
    assert dine_in_data["categories"] == [{"name": "Drinks", "product_ids": ["prod-2"]}]

    takeout_res = client.post(
        "/menus",
        json={
            "channel": "takeout",
            "title": "Takeout Bento",
            "categories": [{"name": "Bento", "product_ids": ["prod-1"]}],
        },
    )
    assert takeout_res.status_code == 201

    dine_in_list = client.get("/menus/dine_in")
    assert dine_in_list.status_code == 200
    assert len(dine_in_list.json()) == 1
    assert dine_in_list.json()[0]["id"] == dine_in_data["id"]

    takeout_list = client.get("/menus/takeout")
    assert takeout_list.status_code == 200
    assert len(takeout_list.json()) == 1
    assert takeout_list.json()[0]["title"] == "Takeout Bento"


def test_create_takeout_menu_rejects_non_takeout_product() -> None:
    app = create_app(product_client=make_product_client())
    client = TestClient(app)

    response = client.post(
        "/menus",
        json={
            "channel": "takeout",
            "title": "Invalid Takeout Menu",
            "categories": [{"name": "Drinks", "product_ids": ["prod-2"]}],
        },
    )

    assert response.status_code == 422


def test_create_menu_rejects_missing_product() -> None:
    app = create_app(product_client=make_product_client())
    client = TestClient(app)

    response = client.post(
        "/menus",
        json={
            "channel": "dine_in",
            "title": "Missing Product Menu",
            "categories": [{"name": "Main", "product_ids": ["prod-missing"]}],
        },
    )

    assert response.status_code == 404


def test_toggle_menu_publish_status() -> None:
    app = create_app(product_client=make_product_client())
    client = TestClient(app)

    create_res = client.post(
        "/menus",
        json={
            "channel": "takeout",
            "title": "Lunch Takeout",
            "categories": [{"name": "Bento", "product_ids": ["prod-1"]}],
        },
    )
    menu_id = create_res.json()["id"]

    unpublish_res = client.patch(
        f"/menus/{menu_id}/publish",
        json={"published": False},
    )
    assert unpublish_res.status_code == 200
    assert unpublish_res.json()["published"] is False
    assert client.get("/menus/takeout").json() == []

    republish_res = client.patch(
        f"/menus/{menu_id}/publish",
        json={"published": True},
    )
    assert republish_res.status_code == 200
    assert republish_res.json()["published"] is True
    assert len(client.get("/menus/takeout").json()) == 1


def test_toggle_publish_missing_menu_returns_404() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.patch(
        "/menus/does-not-exist/publish",
        json={"published": False},
    )

    assert response.status_code == 404


def test_menu_ui_screens() -> None:
    app = create_app(product_client=make_product_client())
    client = TestClient(app)

    client.post(
        "/menus",
        json={
            "channel": "dine_in",
            "title": "Dinner Menu",
            "categories": [{"name": "Drinks", "product_ids": ["prod-2"]}],
        },
    )

    for path in ("/ui/menus", "/ui/menus/editor", "/ui/menus/preview"):
        res = client.get(path)
        assert res.status_code == 200
        assert "メニュー管理" in res.text
