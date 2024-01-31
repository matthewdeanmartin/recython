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
            mock_chat = MagicMock()
            mock_completions = MagicMock()
            mock_client.return_value.chat.completions.create.return_value = mock_chat
            mock_client.return_value.completions.create.return_value = mock_completions
            yield mock_chat, mock_completions


def test_completion(mock_openai_client):
    with temporary_env_var("OPENAI_API_KEY", "FAKE"):
        mock_chat, _ = mock_openai_client
        mock_chat.Choices[0].message.Content = "Test completion response"

        prompt = "Test prompt"
        completion(prompt)


def test_short_completion(mock_openai_client):
    _, mock_completions = mock_openai_client
    mock_completions.Choices[0].text.Strip.return_value = "Test short completion response"

    prompt = "Test prompt"
    short_completion(prompt)
