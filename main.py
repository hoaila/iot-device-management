from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from services import device_store
from utilities import validate_device_registration, validate_command_payload, select_command_template
import ws_client
import http_client

app = FastAPI(title='IoT Device Management API')


class DeviceRegistration(BaseModel):
    serial: str
    model: str
    owner: str
    transport: Optional[str] = 'ws'
    meta: Optional[dict] = {}


class CommandPayload(BaseModel):
    name: Optional[str]
    payload: Optional[dict]
    method: Optional[str]
    path: Optional[str]
    headers: Optional[dict]
    body: Optional[dict]


class OTARequest(BaseModel):
    artifact: str
    path: Optional[str] = '/ota'


@app.post('/devices', status_code=201)
def provision_device(reg: DeviceRegistration):
    ok, err = validate_device_registration(reg.dict())
    if not ok:
        raise HTTPException(status_code=400, detail=err)
    device = device_store.register_device(reg.dict())
    return JSONResponse(status_code=201, content=device)


@app.get('/devices')
def list_devices():
    return device_store.list_devices()


@app.get('/devices/{device_id}')
def get_device(device_id: str):
    d = device_store.get_device(device_id)
    if not d:
        raise HTTPException(status_code=404, detail='device not found')
    return d


@app.post('/devices/{device_id}/commands')
def send_command(device_id: str, cmd: CommandPayload):
    d = device_store.get_device(device_id)
    if not d:
        raise HTTPException(status_code=404, detail='device not found')
    ok, err = validate_command_payload(cmd.dict())
    if not ok:
        raise HTTPException(status_code=400, detail=err)
    # If a template name is provided, resolve it
    payload = cmd.dict()
    if payload.get('name') and not payload.get('payload'):
        template = select_command_template(payload.get('name'))
        if template:
            payload['payload'] = template.get('payload')
    # Choose transport
    transport = d.get('transport', 'ws')
    result = None
    if transport == 'ws':
        result = ws_client.send_command(d, payload)
    else:
        result = http_client.send_command(d, payload)
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('error', 'delivery failed'))
    return {'status': 'ok', 'result': result}


@app.post('/devices/{device_id}/ota')
def trigger_ota(device_id: str, ota: OTARequest):
    d = device_store.get_device(device_id)
    if not d:
        raise HTTPException(status_code=404, detail='device not found')
    # set status to updating
    device_store.update_device_status(device_id, 'updating')
    transport = d.get('transport', 'ws')
    if transport == 'ws':
        res = ws_client.trigger_ota(d, ota.dict())
    else:
        res = http_client.trigger_ota(d, ota.dict())
    if not res.get('success'):
        device_store.update_device_status(device_id, 'update_failed')
        raise HTTPException(status_code=500, detail=res.get('error', 'ota failed'))
    # mark updated
    device_store.update_device_status(device_id, 'updated')
    return {'status': 'ok', 'result': res}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
