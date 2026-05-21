import json
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

import main
from services import device_store

client = TestClient(main.app)


def setup_tmp_store(monkeypatch, tmp_path):
    tmp_file = tmp_path / "devices.json"
    # ensure empty json array
    tmp_file.write_text('[]', encoding='utf-8')
    monkeypatch.setattr(device_store, 'DATA_PATH', str(tmp_file))
    return str(tmp_file)


def test_register_device_and_persist(tmp_path, monkeypatch):
    data_file = setup_tmp_store(monkeypatch, tmp_path)
    payload = {'serial': 'SN123', 'model': 'T1000', 'owner': 'alice', 'transport': 'ws'}
    r = client.post('/devices', json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body.get('serial') == 'SN123'
    # persisted
    assert os.path.exists(data_file)
    with open(data_file, 'r', encoding='utf-8') as f:
        arr = json.load(f)
    assert any(d.get('serial') == 'SN123' for d in arr)


def test_get_device_and_not_found(tmp_path, monkeypatch):
    setup_tmp_store(monkeypatch, tmp_path)
    # register one device
    payload = {'serial': 'GET1', 'model': 'X', 'owner': 'z'}
    r = client.post('/devices', json=payload)
    assert r.status_code == 201
    dev = r.json()
    # GET existing
    r2 = client.get(f"/devices/{dev['id']}")
    assert r2.status_code == 200
    assert r2.json().get('serial') == 'GET1'
    # GET missing
    r3 = client.get('/devices/not-exist')
    assert r3.status_code == 404


def test_send_command_uses_ws_client_and_validation(tmp_path, monkeypatch):
    setup_tmp_store(monkeypatch, tmp_path)
    # Register device with ws transport
    payload = {'serial': 'SNWS', 'model': 'W1', 'owner': 'bob', 'transport': 'ws'}
    r = client.post('/devices', json=payload)
    assert r.status_code == 201
    dev = r.json()

    called = {}

    def fake_send_command(device, command):
        called['device_id'] = device.get('id')
        called['command'] = command
        return {'success': True, 'sent': command.get('payload') or command}

    monkeypatch.setattr(main.ws_client, 'send_command', fake_send_command)

    # valid command by name -> should resolve template if available but still call client
    cmd = {'name': 'Ping', 'payload': {'action': 'ping'}}
    r2 = client.post(f"/devices/{dev['id']}/commands", json=cmd)
    assert r2.status_code == 200
    assert called.get('device_id') == dev['id']

    # invalid payload -> 400
    r3 = client.post(f"/devices/{dev['id']}/commands", json={'invalid': 'x'})
    assert r3.status_code == 400


def test_send_command_http_transport_uses_http_client(tmp_path, monkeypatch):
    setup_tmp_store(monkeypatch, tmp_path)
    # Register HTTP device
    payload = {
        'serial': 'SNHTTP',
        'model': 'H1',
        'owner': 'eve',
        'transport': 'http',
        'meta': {'base_url': 'http://example.local'}
    }
    r = client.post('/devices', json=payload)
    assert r.status_code == 201
    dev = r.json()

    called = {}

    def fake_http_send(device, command):
        called['device_id'] = device.get('id')
        called['command'] = command
        return {'success': True, 'status_code': 200, 'text': 'ok'}

    monkeypatch.setattr(main.http_client, 'send_command', fake_http_send)

    cmd = {'method': 'POST', 'path': '/cmd', 'body': {'x': 1}}
    r2 = client.post(f"/devices/{dev['id']}/commands", json=cmd)
    assert r2.status_code == 200
    assert called.get('device_id') == dev['id']


def test_ota_flow_updates_status_sequence(tmp_path, monkeypatch):
    setup_tmp_store(monkeypatch, tmp_path)
    # Register ws device
    payload = {'serial': 'SNOTA', 'model': 'M', 'owner': 'd', 'transport': 'ws'}
    r = client.post('/devices', json=payload)
    dev = r.json()

    seq = []

    def fake_trigger_ota(device, ota_payload):
        # when called, device status should have been set to 'updating'
        current = device_store.get_device(device['id'])
        seq.append(current.get('status'))
        return {'success': True, 'sent': ota_payload}

    monkeypatch.setattr(main.ws_client, 'trigger_ota', fake_trigger_ota)

    r2 = client.post(f"/devices/{dev['id']}/ota", json={'artifact': 'v1.2'})
    assert r2.status_code == 200
    # seq first recorded status should be 'updating'
    assert seq and seq[0] == 'updating'
    # final status should be 'updated'
    r3 = client.get(f"/devices/{dev['id']}")
    assert r3.status_code == 200
    assert r3.json().get('status') == 'updated'


def test_ota_flow_http_updates_status(tmp_path, monkeypatch):
    setup_tmp_store(monkeypatch, tmp_path)
    # Register http device
    payload = {'serial': 'SNOTAHTTP', 'model': 'MH', 'owner': 'h', 'transport': 'http', 'meta': {'base_url': 'http://x'}}
    r = client.post('/devices', json=payload)
    dev = r.json()

    seq = []

    def fake_http_trigger_ota(device, ota_payload):
        current = device_store.get_device(device['id'])
        seq.append(current.get('status'))
        return {'success': True, 'status_code': 200, 'text': 'ok'}

    monkeypatch.setattr(main.http_client, 'trigger_ota', fake_http_trigger_ota)

    r2 = client.post(f"/devices/{dev['id']}/ota", json={'artifact': 'v2.0'})
    assert r2.status_code == 200
    assert seq and seq[0] == 'updating'
    r3 = client.get(f"/devices/{dev['id']}")
    assert r3.status_code == 200
    assert r3.json().get('status') == 'updated'

