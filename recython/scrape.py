import os

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md


def scrape_to_markdown(url, output_folder):
    # Send an HTTP request to the URL
    response = requests.get(url, timeout=5)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, "html.parser")

    # Identify and extract the main body of the article
    # This might need adjustment depending on the website structure
    main_content = soup.find("div", {"class": "body"})

    if main_content:
        # Convert the content from HTML to Markdown
        markdown_text = md(str(main_content))

        # Create the output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)

        # Define the output file path
        file_name = f"{url.split('/')[-1]}.md"
        output_path = os.path.join(output_folder, file_name)

        # Write the content to the file
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(markdown_text)
        print(f"Content written to {output_path}")
    else:
        print("Main content not found.")


if __name__ == "__main__":
    relevant_urls = [
        "https://cython.readthedocs.io/en/stable/src/tutorial/cython_tutorial.html",
        "https://cython.readthedocs.io/en/stable/src/tutorial/cython_tutorial.html",
        # not all projects need c-interop
        "https://cython.readthedocs.io/en/stable/src/tutorial/external.html",
        "https://cython.readthedocs.io/en/stable/src/tutorial/clibraries.html",
        "https://cython.readthedocs.io/en/stable/src/tutorial/cdef_classes.html",
        "https://cython.readthedocs.io/en/stable/src/tutorial/pxd_files.html",
        "https://cython.readthedocs.io/en/stable/src/tutorial/caveats.html",
        # strings
        "https://cython.readthedocs.io/en/stable/src/tutorial/strings.html",
        "https://cython.readthedocs.io/en/stable/src/tutorial/memory_allocation.html",
        "https://cython.readthedocs.io/en/stable/src/tutorial/pure.html",
        # not all projects need numpy interop
        "https://cython.readthedocs.io/en/stable/src/tutorial/numpy.html",
        "https://cython.readthedocs.io/en/stable/src/tutorial/array.html",
        "https://cython.readthedocs.io/en/stable/src/tutorial/parallelization.html",
    ]
    # Usage
    for url in relevant_urls:
        output_folder = "docs"
        scrape_to_markdown(url, output_folder)
