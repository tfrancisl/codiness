import time
import uuid


def make_session_token(user: str) -> str:
    """Create a new, unique, time-stamped session token for the user."""
    return f"{user}:{int(time.time())}:{uuid.uuid4().hex}"
