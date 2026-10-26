"""Scope boundary without registry I/O (safe for production consumers)."""

RESEARCH_PREFIX = "research-etymon-"
RESEARCH_ONLY = "research_only"


def mapping_scope(ids=(), scope=None) -> str:
    """Research is contagious in mixed mappings; an explicit label cannot downgrade it."""
    if scope not in (None, "production", RESEARCH_ONLY):
        raise ValueError(f"unknown mapping scope: {scope!r}")
    return RESEARCH_ONLY if scope == RESEARCH_ONLY or any(
        str(i).startswith(RESEARCH_PREFIX) for i in ids) else "production"


def research_entry(entry: dict) -> bool:
    return mapping_scope((entry.get("id", ""), entry.get("root_id", "")), entry.get("scope")) == RESEARCH_ONLY
