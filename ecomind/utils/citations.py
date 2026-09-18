"""Citation display helpers."""

from models.schemas import Evidence


def format_source(item: Evidence) -> str:
    return f"[{item.title}]({item.url}) — {item.organization} ({item.year})"
