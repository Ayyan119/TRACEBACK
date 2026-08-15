def count_words(text: str) -> int:
    """Deterministically counts words in a text string based on whitespace boundaries.

    Whitespace, tabs, and newlines are normalized and continuous whitespace
    is treated as a single token separator.

    Examples:
        "" -> 0
        "  hello   world  " -> 2
    """
    if not text:
        return 0
    return len(text.strip().split())
