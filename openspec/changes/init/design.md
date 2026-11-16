# Design: init — menu-management 初期MVP設計

## USDM トレーサビリティ

| USDM 要求ID | 要件概要 | 実装要素 |
| --- | --- | --- |
| `MenuManagement_R01.DM01-01` | `POST /menus` でチャネル（`dine_in` / `takeout`）・カテゴリ・掲載商品リストを持つメニューを作成できる | `main.py` (`POST /menus`), `models.py` (`MenuCreate`, `MenuCategoryInput`, `Menu`), `store.py` (`MenuStore`) |
| `MenuManagement_R01.DM01-02` | `takeout` チャネルに持ち帰り不可商品が指定された場合、HTTP 422 または 400 で拒否する（未存在商品は 404） | `client.py` (`ProductClient`), `main.py` (`POST /menus` 内の検証ロジック) |
| `MenuManagement_R01.DM01-03` | `GET /menus/{channel}` で公開中のメニュー一覧（I-5）を取得できる | `main.py` (`GET /menus/{channel}`, `PATCH /menus/{menu_id}/publish`), `store.py` |

## アーキテクチャ・モジュール構成

- `src/menu_management/models.py`: Pydantic v2 モデル（`Channel`, `MenuCategoryInput`, `MenuCreate`, `MenuPublishUpdate`, `Menu`）。
- `src/menu_management/store.py`: インメモリ `MenuStore`（作成・チャネル別公開一覧取得・公開状態更新）。
- `src/menu_management/client.py`: `ProductClient`（`httpx.Client` をラップし、`base_url` および `transport` を注入可能にして `GET /products/{product_id}` を呼び出す）。
- `src/menu_management/main.py`: `create_app(product_client: ProductClient | None = None)` と `app = create_app()`。`GET /health`, `POST /menus`, `GET /menus/{channel}`, `PATCH /menus/{menu_id}/publish` を提供。

## テスト方針

- `tests/test_menus.py` にて `fastapi.testclient.TestClient` と `httpx.MockTransport` を用い、以下を検証する:
  - 正常系（`POST /menus` 201作成、`GET /menus/{channel}` 公開一覧取得、`GET /health`）
  - `takeout` チャネルで `takeout_available=False` の商品を拒否（HTTP 422）
  - 存在しない商品ID指定時に HTTP 404
  - `PATCH /menus/{menu_id}/publish` による公開/非公開切替と `GET /menus/{channel}` への反映、未存在メニューIDで HTTP 404
