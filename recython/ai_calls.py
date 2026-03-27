import os

import openai

CLIENT = None
DEFAULT_MODEL = os.environ.get("RECYTHON_OPENAI_MODEL", "gpt-4o-mini")


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


def completion(
    prompt: str,
    *,
    model: str | None = None,
    max_completion_tokens: int | None = None,
    temperature: float | None = None,
) -> str:
    client = get_client()
    response = client.chat.completions.create(
        model=model or DEFAULT_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_completion_tokens=max_completion_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content or ""


def short_completion(prompt: str) -> str:
    return completion(prompt, max_completion_tokens=1500)
