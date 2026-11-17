# ruff: noqa: E501
"""HTML UI router for menu-management."""

from html import escape
from typing import Any

import httpx
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from menu_management.client import ProductClient
from menu_management.store import MenuStore

PORTAL_LINKS = [
    ("portal", "ポータル", "/ui/portal"),
    ("product", "商品管理", "/ui/products"),
    ("menu", "メニュー", "/ui/menus"),
    ("guest", "座席・顧客", "/ui/tables"),
    ("order", "注文かんばん", "/ui/orders/kanban"),
    ("accounting", "会計", "/ui/accounting/checkout"),
    ("sales", "売上", "/ui/sales/daily"),
    ("dine_in", "店内QR", "/ui/dine-in/session"),
    ("takeout", "持ち帰り", "/ui/takeout/login"),
]


def _safe_products(product_client: ProductClient | None) -> dict[str, dict[str, Any]]:
    if product_client is None:
        return {}
    try:
        items = product_client.list_products()
        return {str(item["id"]): item for item in items}
    except (httpx.HTTPError, KeyError, TypeError, ValueError):
        return {}


def _render_shell(*, title: str, subtitle: str, active_subtab: str, body_html: str) -> str:
    nav_html = "".join(
        f'<a class="nav-pill{" active" if key == "menu" else ""}" href="{href}">{escape(label)}</a>'
        for key, label, href in PORTAL_LINKS
    )
    subtabs = [
        ("list", "メニュー一覧・公開管理", "/ui/menus"),
        ("editor", "ノーコードメニュー編集", "/ui/menus/editor"),
        ("preview", "端末別プレビュー", "/ui/menus/preview"),
    ]
    subtab_html = "".join(
        f'<a class="subtab{" active" if key == active_subtab else ""}" href="{href}">{escape(label)}</a>'
        for key, label, href in subtabs
    )
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(title)} | まちなか飲食店サポート</title>
  <style>
    :root {{
      --bg: #f8fafc; --surface: #ffffff; --navy: #0f172a; --slate: #334155;
      --muted: #64748b; --border: #e2e8f0; --accent: #ea580c; --accent-soft: #fff7ed;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; background: var(--bg); color: var(--navy); line-height: 1.5;
      font-family: "Noto Sans CJK JP", "Hiragino Kaku Gothic ProN", "Yu Gothic", sans-serif;
    }}
    .topbar {{
      background: var(--navy); color: #fff; padding: 0 24px; height: 54px;
      display: flex; align-items: center; justify-content: space-between; gap: 16px;
    }}
    .brand {{ display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 15px; white-space: nowrap; }}
    .brand-badge {{ background: var(--accent); color: #fff; padding: 2px 8px; border-radius: 6px; font-size: 11px; }}
    .nav-links {{ display: flex; gap: 4px; overflow-x: auto; }}
    .nav-pill {{ color: #cbd5e1; text-decoration: none; font-size: 12px; font-weight: 600; padding: 6px 10px; border-radius: 6px; white-space: nowrap; }}
    .nav-pill.active {{ background: var(--accent); color: #fff; }}
    .subbar {{ background: var(--surface); border-bottom: 1px solid var(--border); padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; gap: 16px; }}
    .subbar h1 {{ margin: 0; font-size: 18px; }}
    .subbar .subtitle {{ margin: 2px 0 0; font-size: 12px; color: var(--muted); }}
    .subtabs {{ display: flex; gap: 8px; }}
    .subtab {{ text-decoration: none; color: var(--slate); font-size: 13px; font-weight: 600; padding: 7px 14px; border-radius: 8px; border: 1px solid var(--border); background: #fff; }}
    .subtab.active {{ background: var(--accent-soft); color: var(--accent); border-color: #fdba74; }}
    .container {{ max-width: 1220px; margin: 0 auto; padding: 20px 24px 28px; }}
    .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 18px; }}
    .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 16px 18px; box-shadow: 0 1px 2px rgba(15,23,42,.04); }}
    .kpi-label {{ font-size: 12px; color: var(--muted); font-weight: 600; }}
    .kpi-value {{ font-size: 24px; font-weight: 800; margin-top: 4px; }}
    .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
    .badge {{ display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 700; }}
    .badge-ok {{ background: #dcfce7; color: #166534; }}
    .badge-off {{ background: #f1f5f9; color: #475569; }}
    .badge-dine {{ background: #dbeafe; color: #1e40af; }}
    .badge-take {{ background: #fef3c7; color: #92400e; }}
    .badge-tag {{ background: #f1f5f9; color: var(--slate); margin: 2px 4px 2px 0; }}
    .btn {{ display: inline-block; text-decoration: none; font-size: 13px; font-weight: 700; padding: 8px 14px; border-radius: 8px; border: none; cursor: pointer; }}
    .btn-primary {{ background: var(--accent); color: #fff; }}
    .btn-secondary {{ background: #f1f5f9; color: var(--slate); border: 1px solid var(--border); }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th {{ text-align: left; padding: 10px 12px; background: #f8fafc; color: var(--muted); font-size: 12px; border-bottom: 1px solid var(--border); }}
    td {{ padding: 11px 12px; border-bottom: 1px solid var(--border); vertical-align: top; }}
    .device-frame {{ border: 8px solid #1e293b; border-radius: 20px; background: #fff; overflow: hidden; }}
    .device-head {{ background: #1e293b; color: #fff; padding: 8px 14px; font-size: 12px; font-weight: 700; display: flex; justify-content: space-between; }}
    .device-body {{ padding: 14px; }}
    .menu-item-card {{ border: 1px solid var(--border); border-radius: 10px; padding: 10px 12px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; }}
    input[type="text"], select {{ width: 100%; padding: 8px 10px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 13px; font-family: inherit; }}
    label {{ font-size: 12px; font-weight: 700; color: var(--slate); display: block; margin-bottom: 5px; }}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="brand">
      <span>🍽️ まちなか飲食店サポート</span>
      <span class="brand-badge">店長・スタッフ共通ポータル</span>
    </div>
    <nav class="nav-links">{nav_html}</nav>
  </header>
  <section class="subbar">
    <div>
      <h1>{escape(title)}</h1>
      <p class="subtitle">{escape(subtitle)}</p>
    </div>
    <div class="subtabs">{subtab_html}</div>
  </section>
  <main class="container">{body_html}</main>
</body>
</html>
"""


def create_ui_router(
    store: MenuStore,
    product_client: ProductClient | None = None,
) -> APIRouter:
    """Create FastAPI router providing HTML UI screens for menu-management."""
    router = APIRouter(tags=["ui"])

    @router.get("/ui/menus", response_class=HTMLResponse)
    def menu_list_page() -> str:
        menus = store.list_all()
        products = _safe_products(product_client)
        published_count = sum(1 for m in menus if m.published)
        dine_count = sum(1 for m in menus if m.channel == "dine_in")
        take_count = sum(1 for m in menus if m.channel == "takeout")

        rows = []
        for m in menus:
            ch_badge = (
                '<span class="badge badge-dine">店内 (dine_in)</span>'
                if m.channel == "dine_in"
                else '<span class="badge badge-take">持ち帰り (takeout)</span>'
            )
            pub_badge = (
                '<span class="badge badge-ok">公開中</span>'
                if m.published
                else '<span class="badge badge-off">非公開</span>'
            )
            cat_html = ""
            for c in m.categories:
                names = [
                    escape(str(products.get(pid, {}).get("name", f"商品#{pid}")))
                    for pid in c.product_ids
                ]
                cat_html += (
                    f'<div style="margin-bottom:4px"><strong>{escape(c.name)}:</strong> '
                    + "".join(f'<span class="badge badge-tag">{n}</span>' for n in names)
                    + "</div>"
                )
            rows.append(
                f"<tr>"
                f"<td><strong>{escape(m.title)}</strong><div style='font-size:11px;color:#64748b'>{escape(m.id[:12])}...</div></td>"
                f"<td>{ch_badge}</td>"
                f"<td>{pub_badge}</td>"
                f"<td>{cat_html or '-'}</td>"
                f'<td><a class="btn btn-secondary" style="padding:4px 10px;font-size:12px" href="/ui/menus/preview">プレビュー</a></td>'
                f"</tr>"
            )
        rows_html = "".join(rows) or (
            '<tr><td colspan="5" style="text-align:center;padding:24px;color:#64748b">メニューがありません。</td></tr>'
        )
        body = f"""
        <div class="kpi-grid">
          <div class="card"><div class="kpi-label">登録メニュー数</div><div class="kpi-value">{len(menus)} 件</div></div>
          <div class="card"><div class="kpi-label">公開中メニュー</div><div class="kpi-value">{published_count} 件</div></div>
          <div class="card"><div class="kpi-label">店内メニュー</div><div class="kpi-value">{dine_count} 件</div></div>
          <div class="card"><div class="kpi-label">持ち帰りメニュー</div><div class="kpi-value">{take_count} 件</div></div>
        </div>
        <div class="card">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
            <h2 style="margin:0;font-size:16px">チャネル別メニュー公開状態</h2>
            <a class="btn btn-primary" href="/ui/menus/editor">＋ ノーコードで新規作成</a>
          </div>
          <table>
            <thead>
              <tr><th>メニュー名</th><th>チャネル</th><th>ステータス</th><th>カテゴリ・割当商品</th><th>プレビュー</th></tr>
            </thead>
            <tbody>{rows_html}</tbody>
          </table>
        </div>
        """
        return _render_shell(
            title="メニュー管理 › 公開メニュー一覧",
            subtitle="店内・持ち帰りメニューの公開切替とカテゴリ構成を一元管理します",
            active_subtab="list",
            body_html=body,
        )

    @router.get("/ui/menus/editor", response_class=HTMLResponse)
    def menu_editor_page() -> str:
        products = _safe_products(product_client)
        prod_cards = []
        for pid, prod in products.items():
            take_tag = (
                '<span class="badge badge-ok">持帰可</span>'
                if prod.get("takeout_available", False)
                else '<span class="badge badge-off">店内のみ</span>'
            )
            prod_cards.append(
                f'<label style="display:flex;align-items:center;justify-content:space-between;'
                f'border:1px solid #e2e8f0;border-radius:8px;padding:8px 10px;margin-bottom:6px;font-weight:500">'
                f'<span><input type="checkbox" class="prod-chk" value="{escape(pid)}" checked> '
                f'<strong>{escape(str(prod.get("name", pid)))}</strong> (¥{int(prod.get("price", 0)):,})</span>'
                f"{take_tag}</label>"
            )
        prod_list_html = "".join(prod_cards) or (
            '<div style="color:#64748b;font-size:13px">商品マスタから取得できる商品がありません（ID直接指定可能）。</div>'
        )
        body = f"""
        <div class="grid-2">
          <div class="card">
            <h2 style="margin:0 0 12px;font-size:16px">ノーコード・メニュー構成ビルダー</h2>
            <div style="margin-bottom:12px">
              <label>配信チャネル</label>
              <select id="m-channel">
                <option value="dine_in">店内メニュー（タブレット / 席QRスマホ）</option>
                <option value="takeout">持ち帰りメニュー（テイクアウト予約）</option>
              </select>
            </div>
            <div style="margin-bottom:12px">
              <label>メニュータイトル</label>
              <input type="text" id="m-title" value="季節のおすすめフェア">
            </div>
            <div style="margin-bottom:12px">
              <label>カテゴリ名</label>
              <input type="text" id="m-cat" value="おすすめ料理">
            </div>
            <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:16px">
              <a class="btn btn-secondary" href="/ui/menus">一覧へ戻る</a>
              <button class="btn btn-primary" onclick="createMenu()">公開メニューを作成する</button>
            </div>
          </div>
          <div class="card">
            <h2 style="margin:0 0 12px;font-size:16px">商品マスタ連携（I-5: 掲載商品選択）</h2>
            <p style="font-size:12px;color:#64748b;margin-top:0">
              ※持ち帰りチャネル選択時、持ち帰り不可商品が含まれると自動バリデーション（HTTP 422）で保護されます。
            </p>
            {prod_list_html}
          </div>
        </div>
        """ + """
        <script>
          async function createMenu() {
            const ids = [...document.querySelectorAll('.prod-chk:checked')].map(el => el.value);
            const res = await fetch('/menus', {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({
                channel: document.getElementById('m-channel').value,
                title: document.getElementById('m-title').value,
                categories: [{name: document.getElementById('m-cat').value, product_ids: ids}]
              })
            });
            if (res.ok) { window.location.href = '/ui/menus'; }
          }
        </script>
        """
        return _render_shell(
            title="メニュー管理 › ノーコードメニュー編集",
            subtitle="商品マスタからドラッグ＆チェック感覚でカテゴリ・公開チャネルを組み立てます",
            active_subtab="editor",
            body_html=body,
        )

    @router.get("/ui/menus/preview", response_class=HTMLResponse)
    def menu_preview_page() -> str:
        products = _safe_products(product_client)
        dine_menus = store.list_published("dine_in")
        take_menus = store.list_published("takeout")

        def render_menu_cards(menus: list[Any], empty_msg: str) -> str:
            if not menus:
                return f'<p style="color:#64748b;font-size:13px">{escape(empty_msg)}</p>'
            html_parts = []
            for m in menus:
                html_parts.append(f'<h3 style="margin:4px 0 10px;font-size:15px">{escape(m.title)}</h3>')
                for cat in m.categories:
                    html_parts.append(
                        f'<div style="font-size:12px;font-weight:700;color:#ea580c;margin:8px 0 4px">'
                        f"{escape(cat.name)}</div>"
                    )
                    for pid in cat.product_ids:
                        prod = products.get(pid, {})
                        pname = str(prod.get("name", f"商品 {pid}"))
                        price = int(prod.get("price", 0))
                        allergens = ", ".join(prod.get("allergens", [])) or "特定アレルゲンなし"
                        html_parts.append(
                            f'<div class="menu-item-card">'
                            f'<div><div style="font-weight:700;font-size:13px">{escape(pname)}</div>'
                            f'<div style="font-size:11px;color:#64748b">{escape(allergens)}</div></div>'
                            f'<div style="font-weight:800;color:#0f172a">¥{price:,}</div>'
                            f"</div>"
                        )
            return "".join(html_parts)

        body = f"""
        <div class="grid-2">
          <div class="device-frame">
            <div class="device-head"><span>📱 店内テーブル・タブレット表示</span><span>dine_in</span></div>
            <div class="device-body">{render_menu_cards(dine_menus, "公開中の店内メニューはありません。")}</div>
          </div>
          <div class="device-frame">
            <div class="device-head"><span>🛍️ スマートフォン持ち帰り表示</span><span>takeout</span></div>
            <div class="device-body">{render_menu_cards(take_menus, "公開中の持ち帰りメニューはありません。")}</div>
          </div>
        </div>
        """
        return _render_shell(
            title="メニュー管理 › 端末別プレビュー",
            subtitle="作成した店内用・持ち帰り用メニューがお客様の端末でどのように表示されるか確認します",
            active_subtab="preview",
            body_html=body,
        )

    return router
