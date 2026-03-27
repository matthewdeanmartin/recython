from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

import recython.ai_calls as ai_calls
from recython.ai_calls import completion, get_client, short_completion
from tests.env_util import temporary_env_var


@pytest.fixture
def mock_openai_client():
    with temporary_env_var("OPENAI_API_KEY", "FAKE"):
        with patch("recython.ai_calls.get_client") as get_client:
            mock_client = MagicMock()
            get_client.return_value = mock_client
            mock_response = SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="Test completion response"))]
            )
            mock_client.chat.completions.create.return_value = mock_response
            yield mock_client


def test_completion(mock_openai_client):
    prompt = "Test prompt"
    result = completion(prompt)

    assert result == "Test completion response"
    mock_openai_client.chat.completions.create.assert_called_once()


def test_short_completion(mock_openai_client):
    prompt = "Test prompt"
    result = short_completion(prompt)

    assert result == "Test completion response"
    mock_openai_client.chat.completions.create.assert_called_once()


def test_get_client_uses_openrouter_settings():
    ai_calls.CLIENTS.clear()

    with temporary_env_var("OPENROUTER_API_KEY", "ROUTER-KEY"):
        with patch.dict("os.environ", {"OPENROUTER_BASE_URL": "https://openrouter.ai/api/v1"}, clear=False):
            with patch("openai.OpenAI") as openai_client:
                client = MagicMock()
                openai_client.return_value = client

                result = get_client("openrouter", timeout=12)

    assert result is client
    openai_client.assert_called_once_with(
        api_key="ROUTER-KEY",
        base_url="https://openrouter.ai/api/v1",
        timeout=12,
    )


def test_completion_retries_retryable_errors():
    response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="Recovered"))])

    with patch("recython.ai_calls.get_client") as get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = [RuntimeError("temporary"), response]
        get_client.return_value = mock_client

        with patch("recython.ai_calls._should_retry", side_effect=[True, False]):
            with patch("time.sleep") as sleep:
                result = completion("prompt", max_retries=2)

    assert result == "Recovered"
    assert mock_client.chat.completions.create.call_count == 2
    sleep.assert_called_once()
