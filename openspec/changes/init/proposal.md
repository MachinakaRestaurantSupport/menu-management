# Proposal: init — メニュー管理（menu-management）初期MVP実装

## Why

店内注文（`dine_in`）と持ち帰り注文（`takeout`）で異なるメニュー構成および公開状態を安全に制御するため、商品マスタ（I-5）と連携してメニュー作成・検証・公開・チャネル別参照を提供する初期MVPを構築する。

## What Changes

- Python パッケージ基盤（`pyproject.toml`）および FastAPI ベースの `menu_management` サービスを新設する。
- メニュー作成（`POST /menus`）、チャネル別公開メニュー取得（`GET /menus/{channel}`）、公開状態切替（`PATCH /menus/{menu_id}/publish`）、ヘルスチェック（`GET /health`）を実装する。
- 商品マスタクライアント（`ProductClient`）により商品存在確認（404）および持ち帰り可否検証（422）を行う。
- 単体試験（`tests/test_menus.py`）を追加する。

## Capabilities

### New Capabilities

- `menu-publishing`: チャネル別メニューの作成・商品検証・公開切替・公開メニュー一覧参照を提供する機能。

### Impact

- 注文ツールは `GET /menus/{channel}` を通じて公開中のチャネル別メニューを取得できる。
- `reference/system-integration/` は読み取り専用とし、変更しない。
