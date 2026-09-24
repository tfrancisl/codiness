def parse_int(text: str, default: int = 0) -> int:
    """Parse an integer, falling back to a default when the text is not a number."""
    try:
        return int(text.strip())
    except ValueError:
        return default


def first_int(items: list[str]) -> int | None:
    """Return the first item that parses as an integer, or None."""
    for item in items:
        try:
            return int(item)
        except ValueError:
            continue
    return None
