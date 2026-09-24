import re
import unicodedata


def slugify(title: str, max_length: int = 60) -> str:
    """Turn an arbitrary title into a URL-safe slug."""
    normalized = unicodedata.normalize("NFKD", title)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_only.lower()).strip("-")
    return slug[:max_length].rstrip("-")
