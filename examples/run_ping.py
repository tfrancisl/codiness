import os


def ping(host: str) -> bool:
    """Return True if the host answers a single ping."""
    return os.system("ping -c 1 " + host) == 0
