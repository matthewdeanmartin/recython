import cython


def extract_code_block(text, start_marker="```cython", end_marker="```"):
    if "```" not in text:
        return text

    # Find the starting position of the first occurrence of start_marker
    start_pos = text.find(start_marker)
    if start_pos == -1:
        # If start_marker is not found, try with '```python'
        start_marker = "```python"
        start_pos = text.find(start_marker)
        if start_pos == -1:
            return text  # Return None if start_marker is still not found

    # Adjust start_pos to the end of the start_marker
    start_pos += len(start_marker)

    # Find the ending position of the first occurrence of end_marker, starting from the end of the string
    end_pos = text.rfind(end_marker)
    if end_pos == -1 or end_pos <= start_pos:
        return text  # Return None if end_marker is not found or is before the start_marker

    # Extract the text between the start_marker and end_marker
    code_block = text[start_pos:end_pos].strip()

    return code_block


def run():
    """Example code"""
    if cython.compiled:
        print("Yep, I'm compiled.")
    else:
        print("Just a lowly interpreted script.")
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
