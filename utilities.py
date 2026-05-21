from datetime import datetime


DEFAULT_COMMANDS = [
    {
        "name": "Ping",
        "payload": {
            "action": "ping",
            "timestamp": "2026-03-27T12:00:00Z",
        },
    },
    {
        "name": "Login",
        "payload": {
            "action": "login",
            "username": "demo_user",
            "token": "replace-me",
        },
    },
    {
        "name": "Subscribe",
        "payload": {
            "action": "subscribe",
            "channel": "events",
        },
    },
    {
        "name": "Echo",
        "payload": {
            "action": "echo",
            "message": "hello from tkinter client",
        },
    },
    {
        "name": "HTTP POST sample",
        "payload": {
            "method": "POST",
            "path": "/api/commands",
            "headers": {
                "Content-Type": "application/json",
            },
            "body": {
                "action": "status",
            },
            "timeout": 10,
        },
    },
]


class AppLogger:
    def __init__(self, callback) -> None:
        self.callback = callback

    def log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.callback(f"[{timestamp}] {message}\n")

import json
from typing import Tuple, Optional


def validate_device_registration(payload: dict) -> Tuple[bool, Optional[str]]:
    required = ['serial', 'model', 'owner']
    for r in required:
        if not payload.get(r):
            return False, f"missing required field: {r}"
    # optional transport
    transport = payload.get('transport', 'ws')
    if transport not in ('ws', 'http'):
        return False, 'transport must be "ws" or "http"'
    return True, None


def validate_command_payload(payload: dict) -> Tuple[bool, Optional[str]]:
    if not isinstance(payload, dict):
        return False, 'command must be a JSON object'
    if not payload.get('name') and not payload.get('payload') and not payload.get('method'):
        return False, 'command must include either "name", "payload", or HTTP fields like "method"'
    return True, None


def load_default_commands(path: str = 'default_commands.json') -> list:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def select_command_template(name: str) -> Optional[dict]:
    cmds = load_default_commands()
    for c in cmds:
        if c.get('name') == name:
            return c
    return None

import json
from typing import Tuple, Optional


def validate_device_registration(payload: dict) -> Tuple[bool, Optional[str]]:
    required = ['serial', 'model', 'owner']
    for r in required:
        if not payload.get(r):
            return False, f"missing required field: {r}"
    # optional transport
    transport = payload.get('transport', 'ws')
    if transport not in ('ws', 'http'):
        return False, 'transport must be "ws" or "http"'
    return True, None


def validate_command_payload(payload: dict) -> Tuple[bool, Optional[str]]:
    if not isinstance(payload, dict):
        return False, 'command must be a JSON object'
    if not payload.get('name') and not payload.get('payload') and not payload.get('method'):
        return False, 'command must include either "name", "payload", or HTTP fields like "method"'
    return True, None


def load_default_commands(path: str = 'default_commands.json') -> list:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def select_command_template(name: str) -> Optional[dict]:
    cmds = load_default_commands()
    for c in cmds:
        if c.get('name') == name:
            return c
    return None
