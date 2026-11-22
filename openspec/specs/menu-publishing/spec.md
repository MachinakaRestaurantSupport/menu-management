# menu-publishing Specification

## Purpose
店内および持ち帰りチャネル別のメニューを作成し、商品マスタ連携による存在・持ち帰り可否検証と公開状態の制御・参照を提供する。

## Requirements

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

### Requirement: サブモジュール参照のコミット指定管理

本リポジトリは `.gitmodules` に `branch` 設定を持たせず `reference/system-integration` を確定コミット SHA（gitlink）指定で管理しなければならず（MUST）、`reference/system-integration/` 配下を読み取り専用として直接変更してはならない（SHALL）。

#### Scenario: サブモジュール参照の更新とマージ

- **WHEN** `system-integration` の確定コミット SHA（`<commit-sha>`）を `reference/system-integration` にチェックアウトし、`system-integration` PR の Merge commit マージ後に本リポジトリの PR を `main` にマージするとき
- **THEN** `.gitmodules` の書き換えやマージ後の `main` 戻し作業なしで、正しい仕様・画像参照を維持したままマージが完了する（SHALL）
