# menu-management

商品情報から、タブレット・スマートフォン対応の店内メニューや持ち帰りメニューをノーコードで作成・公開するツールです。  
店長・スタッフ共通ポータル（[ポータル画面イメージ](reference/system-integration/docs/images/portal/01-portal-dashboard.png)）と連携し、持ち帰りメニューへ持ち帰り不可商品が混入しないよう商品マスタ（I-5）と整合チェックを行います。

## 画面遷移図

縮小画面キャプチャを用いた `menu-management` の画面遷移図です（draw.io 編集用ソース: [transition.drawio](reference/system-integration/docs/images/menu_management/transition.drawio)）。

![menu-management 画面遷移図](reference/system-integration/docs/images/menu_management/transition.svg)

## 代表機能イメージ

### 1. メニュー一覧・公開状態管理 (`GET /ui/menus`)
登録済みの店内メニュー（`dine_in`）および持ち帰りメニュー（`takeout`）の公開ステータス、カテゴリ別の割当商品一覧を確認できます。

![メニュー一覧・公開管理](reference/system-integration/docs/images/menu_management/01-menu-list.png)

### 2. ノーコードメニュー編集 (`GET /ui/menus/editor`)
配信チャネルとカテゴリ名を指定し、商品マスタから掲載商品をチェック選択するだけで公開メニューを作成（`POST /menus`）できます。

![ノーコードメニュー編集](reference/system-integration/docs/images/menu_management/02-menu-editor.png)

### 3. 端末別プレビュー (`GET /ui/menus/preview`)
店内テーブルのタブレット表示と、お客様スマートフォンの持ち帰りメニュー表示を左右に並べて確認できます。

![端末別プレビュー](reference/system-integration/docs/images/menu_management/03-menu-preview.png)

## 提供 API・UI エンドポイント

| 種別 | メソッド & パス | 機能概要 |
|---|---|---|
| API | `GET /health` | ヘルスチェック |
| API | `POST /menus` | メニュー作成・商品マスタ整合検証 (I-5) |
| API | `GET /menus/{channel}` | 公開中メニュー取得（`dine_in` / `takeout`） |
| API | `PATCH /menus/{menu_id}/publish` | メニューの公開/非公開切り替え |
| UI | `GET /ui/menus` | メニュー一覧・公開管理画面 |
| UI | `GET /ui/menus/editor` | ノーコードメニュー編集画面 |
| UI | `GET /ui/menus/preview` | 端末別プレビュー画面 |

## テスト・静的解析の実行

```bash
../.venv/bin/python3 -m pytest -v
../.venv/bin/ruff check .
```
