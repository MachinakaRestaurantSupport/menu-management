"""In-memory store for menus."""

import uuid

from menu_management.models import Channel, Menu, MenuCreate


class MenuStore:
    """In-memory repository for managing menus."""

    def __init__(self) -> None:
        self._menus: dict[str, Menu] = {}

    def create(self, payload: MenuCreate) -> Menu:
        """Create and store a new published menu."""
        menu_id = str(uuid.uuid4())
        menu = Menu(
            id=menu_id,
            channel=payload.channel,
            title=payload.title,
            published=True,
            categories=list(payload.categories),
        )
        self._menus[menu_id] = menu
        return menu

    def list_published(self, channel: Channel) -> list[Menu]:
        """Return all published menus for the given channel."""
        return [
            menu
            for menu in self._menus.values()
            if menu.channel == channel and menu.published
        ]

    def list_all(self) -> list[Menu]:
        """Return all stored menus regardless of publication status."""
        return list(self._menus.values())

    def set_published(self, menu_id: str, published: bool) -> Menu | None:
        """Update publication status of a menu, returning None if not found."""
        existing = self._menus.get(menu_id)
        if existing is None:
            return None
        updated = existing.model_copy(update={"published": published})
        self._menus[menu_id] = updated
        return updated
