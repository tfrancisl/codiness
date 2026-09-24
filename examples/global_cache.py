_CACHE: dict[str, bytes] = {}
hits = 0


def load_asset(name: str) -> bytes:
    """Return an asset's bytes, caching it in module state after the first read."""
    global hits
    if name in _CACHE:
        hits += 1
        return _CACHE[name]
    with open(f"assets/{name}", "rb") as fh:
        data = fh.read()
    _CACHE[name] = data
    return data
