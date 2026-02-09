from config import Config


def truncate(value, max_len=None):
    """Truncate a string representation to max_len characters."""
    max_len = max_len or Config.LOG_TRUNCATE
    s = str(value)
    if max_len == 0 or len(s) <= max_len:
        return s
    return s[:max_len] + f"... ({len(s)} chars total)"
