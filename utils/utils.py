

# ===== Helper: safe blob name =====
def sanitize(s: str) -> str:
    INVALID_CHARS = '<>:"/\\|?*'
    s = s.replace(" ", "_")
    for ch in INVALID_CHARS:
        s = s.replace(ch, "_")
    return s
