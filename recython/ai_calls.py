import os

import openai

CLIENT = None


def get_client() -> openai.OpenAI:
    global CLIENT
    if CLIENT is None:
        client = openai.OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),  # this is also the default, it can be omitted
        )
        CLIENT = client
    return CLIENT


PURE_STYLE = 1
CLASSIC_STYLE = 2


def completion(prompt: str) -> str:
    client = get_client()
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
    return completion.choices[0].message.content or ""


def short_completion(prompt: str) -> str:
    client = get_client()
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
