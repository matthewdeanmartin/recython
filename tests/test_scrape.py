from unittest import mock

from recython.scrape import download_all


def test_download_all(tmp_path):
    with mock.patch("requests.get") as mock_get_patcher:
        mock_response = mock_get_patcher.return_value
        mock_response.raise_for_status.return_value = None
        mock_response.text = "<div class='body'>Test content</div>"

    download_all(tmp_path)
