import unittest
from unittest.mock import MagicMock, patch

from http_client import HttpClient


class DummyLogger:
    def __init__(self):
        self.messages = []

    def log(self, message: str) -> None:
        self.messages.append(message)


class TestHttpClient(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = DummyLogger()
        self.client = HttpClient(self.logger)

    @patch('http_client.requests.request')
    @patch('http_client.threading.Thread')
    def test_send_request_logs_http_response(self, mock_thread, mock_request):
        response = MagicMock()
        response.status_code = 200
        response.reason = 'OK'
        response.text = 'done'
        mock_request.return_value = response

        def make_thread(*args, **kwargs):
            target = kwargs['target']
            thread = MagicMock()
            thread.start.side_effect = lambda: target()
            return thread

        mock_thread.side_effect = make_thread

        request_data = {
            'method': 'GET',
            'path': '/api/test',
            'headers': {'Accept': 'application/json'},
            'body': {'hello': 'world'},
            'timeout': 5,
        }

        self.client.send_request('http://localhost:8765', request_data)

        mock_request.assert_called_once_with(
            method='GET',
            url='http://localhost:8765/api/test',
            headers={'Accept': 'application/json'},
            json={'hello': 'world'},
            timeout=5,
        )
        self.assertTrue(any('HTTP response: status=200' in msg for msg in self.logger.messages))

    @patch('http_client.requests.request')
    @patch('http_client.threading.Thread')
    def test_send_request_empty_base_url_logs_error(self, mock_thread, mock_request):
        mock_thread.return_value = MagicMock()

        self.client.send_request('', {'method': 'GET', 'path': '/'})

        self.assertTrue(any('HTTP Base URL is empty.' in msg for msg in self.logger.messages))
        mock_request.assert_not_called()

    @patch('http_client.requests.request')
    @patch('http_client.threading.Thread')
    def test_send_request_invalid_timeout_uses_default(self, mock_thread, mock_request):
        response = MagicMock()
        response.status_code = 200
        response.reason = 'OK'
        response.text = 'done'
        mock_request.return_value = response

        def make_thread(*args, **kwargs):
            target = kwargs['target']
            thread = MagicMock()
            thread.start.side_effect = lambda: target()
            return thread

        mock_thread.side_effect = make_thread

        request_data = {
            'method': 'POST',
            'path': '/api/test',
            'headers': {},
            'body': {'hello': 'world'},
            'timeout': -5,
        }

        self.client.send_request('http://localhost:8765', request_data)

        mock_request.assert_called_once()
        self.assertEqual(mock_request.call_args[1]['timeout'], 10)
        self.assertTrue(any('Invalid HTTP timeout' in msg for msg in self.logger.messages))
