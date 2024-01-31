from recython.tidy import extract_code_block, run


def test_extract_code_block():
    # Test the function
    sample_text = """
    Some random text
    ```cython
    def hello_world():
        print("Hello, World!")
    ```
    """
    assert extract_code_block(sample_text) == 'def hello_world():\n        print("Hello, World!")'


def test_run():
    run()
