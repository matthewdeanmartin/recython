from pathlib import Path
from unittest.mock import MagicMock, patch

from recython.classic_style import cythonize_classic_project
from tests.env_util import temporary_env_var


def test_cythonize_project(tmp_path):
    with temporary_env_var("OPENAI_API_KEY", "FAKE"):
        with patch("recython.ai_calls.get_client") as get_client:
            with patch("recython.ai_calls.completion") as completion:
                mock_client = MagicMock()
                get_client.return_value = mock_client
                completion.return_value = "Test completion response"

                folder_path = Path("./../examples/src_hangman/hangman")
                assert folder_path.exists()
                target_folder = tmp_path
                never_translate = [
                    "__init__",
                ]
                written = cythonize_classic_project(folder_path, target_folder, never_translate)
                assert written
                for file in written:
                    assert file.exists()
                    assert file.read_text() == "Test completion response"
