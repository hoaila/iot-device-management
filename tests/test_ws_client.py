import unittest
from unittest.mock import MagicMock, patch

from ws_client import WebSocketManager


class DummyLogger:
    def __init__(self):
        self.messages = []

    def log(self, message: str) -> None:
        self.messages.append(message)


class TestWebSocketManager(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = DummyLogger()
        self.manager = WebSocketManager(logger=self.logger)

    def test_connect_without_url_logs_error(self):
        self.manager.connect('')
        self.assertTrue(any('WebSocket URL is empty.' in msg for msg in self.logger.messages))

    def test_connect_when_already_connected_logs(self):
        self.manager.connected = True
        self.manager.connect('ws://localhost:8765/ws')
        self.assertTrue(any('WebSocket is already connected.' in msg for msg in self.logger.messages))

    @patch('ws_client.WebSocketApp')
    @patch('ws_client.threading.Thread')
    def test_connect_starts_websocket_thread(self, mock_thread, mock_websocket):
        ws_app_instance = MagicMock()
        mock_websocket.return_value = ws_app_instance

        def make_thread(*args, **kwargs):
            target = kwargs['target']
            thread = MagicMock()
            thread.start.side_effect = lambda: target()
            return thread

        mock_thread.side_effect = make_thread

        self.manager.connect('ws://localhost:8765/ws')

        mock_websocket.assert_called_once()
        self.assertTrue(any('Connecting to WebSocket' in msg for msg in self.logger.messages))

    def test_send_json_without_connection_logs(self):
        self.manager.send_json({'test': True})
        self.assertTrue(any('Cannot send via WebSocket: not connected.' in msg for msg in self.logger.messages))

    def test_send_json_when_connected(self):
        self.manager.connected = True
        self.manager.ws_app = MagicMock()
        self.manager.send_json({'test': True})
        self.manager.ws_app.send.assert_called_once()
        self.assertTrue(any('Sent WebSocket message' in msg for msg in self.logger.messages))
