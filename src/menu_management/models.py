"""Domain models for menu management."""

from typing import Literal

from pydantic import BaseModel, Field

Channel = Literal["dine_in", "takeout"]


class MenuCategoryInput(BaseModel):
    """Input and stored representation of a menu category."""

    name: str
    product_ids: list[str] = Field(default_factory=list)


class MenuCreate(BaseModel):
    """Request payload for creating a menu."""

    channel: Channel
    title: str
    categories: list[MenuCategoryInput] = Field(default_factory=list)


class MenuPublishUpdate(BaseModel):
    """Request payload for toggling menu publication status."""

    published: bool


class Menu(BaseModel):
    """Menu resource representation."""

    id: str
    channel: Channel
    title: str
    published: bool = True
    categories: list[MenuCategoryInput] = Field(default_factory=list)
