import cython

from recython.benchmark_utils import CaptureOutput as capture_output


def is_compiled():
    """Is this module compiled?"""
    return cython.compiled


def has_code_fence(text: str) -> bool:
    """Return True if *text* contains at least one fenced code block (``` ... ```)."""
    return "```" in text


def extract_code_block(text: str, start_marker: str = "```cython", end_marker: str = "```") -> str:
    """Extract the first fenced code block from LLM output.

    Tries ``start_marker`` first (default ``cython``), then falls back to
    ``python``, then any triple-backtick fence.  Returns the raw ``text`` if
    no fence is found, so callers always get a non-empty string when the LLM
    returned content at all.
    """
    if "```" not in text:
        return text

    # Try each candidate opener in priority order.
    candidates = [start_marker, "```python", "```"]
    chosen_start = -1
    chosen_marker = ""
    for marker in candidates:
        pos = text.find(marker)
        if pos != -1:
            # Make sure it is actually an opening fence (next char is newline or end-of-line).
            after = pos + len(marker)
            if after >= len(text) or text[after] in ("\n", "\r", " ", "\t"):
                chosen_start = pos + len(marker)
                chosen_marker = marker
                break

    if chosen_start == -1:
        return text

    # Skip to the end of the opening line.
    newline = text.find("\n", chosen_start)
    if newline != -1:
        chosen_start = newline + 1

    # Find the matching closing fence — the first bare ``` on its own line after chosen_start.
    search_from = chosen_start
    end_pos = -1
    while True:
        idx = text.find(end_marker, search_from)
        if idx == -1:
            break
        # Accept only if this ``` is at the start of a line (or after only whitespace).
        line_start = text.rfind("\n", 0, idx)
        prefix = text[line_start + 1 : idx]
        if prefix.strip() == "":
            end_pos = idx
            break
        search_from = idx + len(end_marker)

    if end_pos == -1 or end_pos <= chosen_start:
        return text

    return text[chosen_start:end_pos].strip()


def run():
    with capture_output() as _captured:
        # Test the function
        sample_text = """
        Some random text
        ```cython
        def hello_world():
            print("Hello, World!")
        ```
        """
        print(extract_code_block(sample_text))


if __name__ == "__main__":
    run()
