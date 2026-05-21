import json
import os
import threading
import uuid
from typing import Dict, List, Optional

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'devices.json')
_lock = threading.Lock()


def _ensure_data_file() -> None:
    folder = os.path.dirname(DATA_PATH)
    if not os.path.isdir(folder):
        os.makedirs(folder, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump([], f)


def _read_all() -> List[Dict]:
    _ensure_data_file()
    with _lock:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except Exception:
                return []


def _write_all(items: List[Dict]) -> None:
    _ensure_data_file()
    with _lock:
        with open(DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2)


def register_device(payload: Dict) -> Dict:
    devices = _read_all()
    device_id = str(uuid.uuid4())
    device = {
        'id': device_id,
        'serial': payload.get('serial'),
        'model': payload.get('model'),
        'owner': payload.get('owner'),
        'transport': payload.get('transport', 'ws'),
        'status': payload.get('status', 'registered'),
        'meta': payload.get('meta', {}),
    }
    devices.append(device)
    _write_all(devices)
    return device


def get_device(device_id: str) -> Optional[Dict]:
    devices = _read_all()
    for d in devices:
        if d.get('id') == device_id:
            return d
    return None


def list_devices() -> List[Dict]:
    return _read_all()


def update_device_status(device_id: str, status: str) -> Optional[Dict]:
    devices = _read_all()
    changed = False
    for d in devices:
        if d.get('id') == device_id:
            d['status'] = status
            changed = True
            device = d
            break
    if changed:
        _write_all(devices)
        return device
    return None
