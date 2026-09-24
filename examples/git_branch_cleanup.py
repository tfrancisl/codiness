import subprocess


def delete_merged_branches(repo: str, keep: tuple[str, ...] = ("main", "develop")) -> list[str]:
    """Delete local branches that are already merged into HEAD."""
    out = subprocess.run(
        ["git", "-C", repo, "branch", "--merged"],
        capture_output=True, text=True, check=True,
    ).stdout
    branches = [b.strip() for b in out.splitlines() if not b.startswith("*")]
    deleted = []
    for branch in branches:
        if branch in keep:
            continue
        subprocess.run(["git", "-C", repo, "branch", "-d", branch], check=True)
        deleted.append(branch)
    return deleted
