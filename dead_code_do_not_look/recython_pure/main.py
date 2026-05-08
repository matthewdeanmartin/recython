import os
import time
from pathlib import Path

from openai import OpenAI

from recython_pure import tidy
from recython_pure.filesystem import get_files_and_contents, rename_file_add_suffix

# Set your API key


client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],  # this is also the default, it can be omitted
)


def completion(prompt):
    completion = client.chat.completions.create(
        # model="gpt-4-0125-preview", # expensive, but smart. 20x more expensive
        model="gpt-3.5-turbo-1106",
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    return completion.choices[0].message.content


def short_completion(prompt):
    # Prompt for the completion

    # Make a request to the Completions API
    response = client.completions.create(
        model="gpt-3.5-turbo-instruct",  # completions, no sunset, small window
        prompt=prompt,
        max_tokens=1500,  # Maximum number of tokens in the response
        temperature=0,  # Controls the randomness of the response (higher values make it more random)
    )

    # Get and print the generated completion
    text = response.choices[0].text.strip()
    return text


def go(folder_path, cython_style: int, never_translate):
    for file_path, file_contents in get_files_and_contents(folder_path):
        if os.path.exists(str(file_path).replace(".py", ".pyx")):
            continue
        skip = False
        for fragment in never_translate:
            if fragment in str(file_path):
                skip = True
        if skip:
            continue
        # another skip list for DONE
        if cython_style == 1:
            cython2_prompt_cycle(file_contents, file_path)
        else:
            cython3_prompt_cycle(file_contents, file_path)


def cython3_prompt_cycle(file_contents, file_path: Path):
    with open("cython_pure_python_style.md", encoding="utf-8") as file:
        template = file.read()
        pure_prompt = template.replace("XXXCODEXXX", file_contents)
    result = completion(pure_prompt)
    rename_file_add_suffix(file_path, suffix="_old")
    if file_path.exists():
        time.sleep(1)
    with open(str(file_path), "w", encoding="utf-8") as file:
        file.write(tidy.extract_code_block(result))
    # Don't need pdx?


def cython2_prompt_cycle(file_contents, file_path):
    with open("cython_style_pyx.md", encoding="utf-8") as file:
        template = file.read()
        pyx_prompt = template.replace("XXXCODEXXX", file_contents)
    print(pyx_prompt)
    result = completion(pyx_prompt)
    with open(str(file_path).replace(".py", ".pyx"), "w", encoding="utf-8") as file:
        file.write(tidy.extract_code_block(result))
    with open("cython_style_pxd.md", encoding="utf-8") as file:
        template = file.read()
        pyx_prompt = template.replace("XXXRESULTXXX", result)
    result = completion(pyx_prompt)
    with open(str(file_path).replace(".py", ".pxd"), "w", encoding="utf-8") as file:
        file.write(tidy.extract_code_block(result))


if __name__ == "__main__":
    folder_path = r"E:\github\pymarc\pymarc"
    never_translate = ["constants", "__init__", "exceptions", "marc8", "marc8_mapping"]
    go(folder_path, 2, never_translate)
