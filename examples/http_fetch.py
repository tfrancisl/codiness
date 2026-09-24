import json
import urllib.request


def fetch_user(user_id: int, base_url: str = "https://api.example.com") -> dict:
    """Fetch a user record from the remote API."""
    req = urllib.request.Request(
        f"{base_url}/users/{user_id}",
        headers={"Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)
