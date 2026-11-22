## Purpose

店内および持ち帰りチャネル別のメニューを作成し、商品マスタ連携による存在・持ち帰り可否検証と公開状態の制御・参照を提供する。

## ADDED Requirements

### Requirement: メニュー作成と検証

`POST /menus` でメニューを作成できなければならない（SHALL）。

#### Scenario: 持ち帰り不可の拒否

- **WHEN** `takeout` で持ち帰り不可商品を指定する
- **THEN** HTTP 422 を返さなければならない（MUST）

### Requirement: 公開メニュー参照

`GET /menus/{channel}` で公開中メニュー一覧を返し、`PATCH /menus/{menu_id}/publish` で公開状態を切り替えなければならない（SHALL）。

#### Scenario: 公開一覧取得

- **WHEN** `GET /menus/{channel}` を呼ぶ
- **THEN** `published=True` の一覧を返す
