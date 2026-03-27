from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from recython.ai_calls import completion, short_completion
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
