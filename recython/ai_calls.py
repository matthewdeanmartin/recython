import os
import time

import openai

CLIENTS: dict[tuple[str, str | None, str | None, float], openai.OpenAI] = {}
DEFAULT_MODEL = os.environ.get("RECYTHON_OPENAI_MODEL", "gpt-4o-mini")
DEFAULT_TIMEOUT = float(os.environ.get("RECYTHON_OPENAI_TIMEOUT", "60"))
DEFAULT_MAX_RETRIES = int(os.environ.get("RECYTHON_OPENAI_MAX_RETRIES", "3"))


def _provider_settings(provider: str) -> tuple[str | None, str | None]:
    if provider == "openrouter":
        api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
        base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        return api_key, base_url
    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        base_url = os.environ.get("OPENAI_BASE_URL")
        return api_key, base_url
    raise ValueError(f"Unsupported provider '{provider}'.")


def get_client(provider: str = "openai", *, timeout: float = DEFAULT_TIMEOUT) -> openai.OpenAI:
    api_key, base_url = _provider_settings(provider)
    if not api_key:
        env_name = "OPENROUTER_API_KEY" if provider == "openrouter" else "OPENAI_API_KEY"
        raise ValueError(f"Missing API key for provider '{provider}'. Set {env_name}.")
    cache_key = (provider, api_key, base_url, timeout)
    client = CLIENTS.get(cache_key)
    if client is None:
        client = openai.OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
        CLIENTS[cache_key] = client
    return client


def _should_retry(exc: Exception) -> bool:
    return isinstance(
        exc,
        (
            openai.APIConnectionError,
            openai.APITimeoutError,
            openai.RateLimitError,
            openai.InternalServerError,
        ),
    )


PURE_STYLE = 1
CLASSIC_STYLE = 2


def completion(
    prompt: str,
    *,
    provider: str = "openai",
    model: str | None = None,
    max_completion_tokens: int | None = None,
    temperature: float | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    max_retries: int = DEFAULT_MAX_RETRIES,
) -> str:
    client = get_client(provider, timeout=timeout)
    for attempt in range(1, max_retries + 1):
        try:
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
            message = response.choices[0].message.content
            if isinstance(message, str):
                return message
            if isinstance(message, list):
                return "".join(
                    part.get("text", "") if isinstance(part, dict) else getattr(part, "text", "") for part in message
                )
            return ""
        except Exception as exc:
            if attempt >= max_retries or not _should_retry(exc):
                raise
            time.sleep(min(2 ** (attempt - 1), 8))


def short_completion(prompt: str) -> str:
    return completion(prompt, max_completion_tokens=1500)
