import requests


def get_repo_stars(owner: str, repo: str, token: str | None = None) -> int:
    """Return the star count of a GitHub repository."""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}", headers=headers, timeout=10
    )
    resp.raise_for_status()
    return resp.json()["stargazers_count"]
