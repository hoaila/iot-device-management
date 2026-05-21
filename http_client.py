import threading

import requests


class HttpClient:
    def __init__(self, logger) -> None:
        self.logger = logger

    def send_request(self, base_url: str, request_data: dict) -> None:
        if not base_url:
            self.logger.log("HTTP Base URL is empty.")
            return

        method = str(request_data.get("method", "POST")).upper()
        path = str(request_data.get("path", "/"))
        headers = request_data.get("headers", {})
        body = request_data.get("body", None)
        timeout = request_data.get("timeout", 10)

        url = f"{base_url.rstrip('/')}{path if path.startswith('/') else '/' + path}"
        self.logger.log(f"Sending HTTP request: {method} {url}")

        def do_request() -> None:
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=body,
                    timeout=timeout,
                )
                preview = response.text[:2000]
                self.logger.log(
                    f"HTTP response: status={response.status_code}, "
                    f"reason={response.reason}, body={preview}"
                )
            except Exception as exc:
                self.logger.log(f"HTTP request error: {exc}")

        threading.Thread(target=do_request, daemon=True).start()

# Helper functions for device provisioning/commands

def send_command(device: dict, command: dict) -> dict:
    """Send a command to an HTTP-backed device. Returns a dict with success and message.
    This is a thin helper; tests should mock this function.
    """
    base_url = device.get('meta', {}).get('endpoint') or device.get('meta', {}).get('base_url')
    if not base_url:
        return {'success': False, 'error': 'device has no http endpoint'}
    try:
        method = command.get('method', 'POST')
        path = command.get('path', '/')
        headers = command.get('headers', {})
        body = command.get('body')
        timeout = command.get('timeout', 5)
        url = f"{base_url.rstrip('/')}{path if path.startswith('/') else '/' + path}"
        resp = requests.request(method=method, url=url, headers=headers, json=body, timeout=timeout)
        return {'success': True, 'status_code': resp.status_code, 'text': resp.text}
    except Exception as exc:
        return {'success': False, 'error': str(exc)}


def trigger_ota(device: dict, ota_payload: dict) -> dict:
    """Trigger OTA on an HTTP device. Simplified; tests should mock.
    """
    base_url = device.get('meta', {}).get('endpoint') or device.get('meta', {}).get('base_url')
    if not base_url:
        return {'success': False, 'error': 'device has no http endpoint'}
    try:
        path = ota_payload.get('path', '/ota')
        url = f"{base_url.rstrip('/')}{path if path.startswith('/') else '/' + path}"
        resp = requests.post(url, json=ota_payload.get('body', {}), timeout=10)
        return {'success': True, 'status_code': resp.status_code, 'text': resp.text}
    except Exception as exc:
        return {'success': False, 'error': str(exc)}

# Helper functions for device provisioning/commands

def send_command(device: dict, command: dict) -> dict:
    """Send a command to an HTTP-backed device. Returns a dict with success and message.
    This is a thin helper; tests should mock this function.
    """
    base_url = device.get('meta', {}).get('endpoint') or device.get('meta', {}).get('base_url')
    if not base_url:
        return {'success': False, 'error': 'device has no http endpoint'}
    try:
        method = command.get('method', 'POST')
        path = command.get('path', '/')
        headers = command.get('headers', {})
        body = command.get('body')
        timeout = command.get('timeout', 5)
        url = f"{base_url.rstrip('/')}{path if path.startswith('/') else '/' + path}"
        resp = requests.request(method=method, url=url, headers=headers, json=body, timeout=timeout)
        return {'success': True, 'status_code': resp.status_code, 'text': resp.text}
    except Exception as exc:
        return {'success': False, 'error': str(exc)}


def trigger_ota(device: dict, ota_payload: dict) -> dict:
    """Trigger OTA on an HTTP device. Simplified; tests should mock.
    """
    base_url = device.get('meta', {}).get('endpoint') or device.get('meta', {}).get('base_url')
    if not base_url:
        return {'success': False, 'error': 'device has no http endpoint'}
    try:
        path = ota_payload.get('path', '/ota')
        url = f"{base_url.rstrip('/')}{path if path.startswith('/') else '/' + path}"
        resp = requests.post(url, json=ota_payload.get('body', {}), timeout=10)
        return {'success': True, 'status_code': resp.status_code, 'text': resp.text}
    except Exception as exc:
        return {'success': False, 'error': str(exc)}
