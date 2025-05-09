import sys
import os
from os.path import dirname, abspath
sys.path.insert(0, dirname(dirname(abspath(__file__))))
os.system('redis-server.exe')

import subprocess


def start_celery_worker():
    cmd = [
        sys.executable,  # путь к текущему интерпретатору Python
        '-m', 'celery',
        '-A', 'app.clr.celery_app',
        'worker',
        '--pool=eventlet',
        '--loglevel=info'
    ]
    subprocess.Popen(cmd)


start_celery_worker()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from api.endpoints import router as router_users
from websockt.websocket import html, manager, execute_command
from clr.celery_app import binarize_image
import redis
import json
import asyncio

app = FastAPI()
redis_conn = redis.StrictRedis()


@app.get("/")
async def home_page():
    return HTMLResponse(html)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await websocket.accept()
    pubsub = redis_conn.pubsub()  # Подписка на Redis канал
    pubsub.subscribe(f'ws_{client_id}')

    async def listen_redis():
        while True:
            message = pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                await websocket.send_text(message['data'].decode())
            await asyncio.sleep(0.01)

    listener = asyncio.create_task(listen_redis())

    try:
        while True:
            data = await websocket.receive_text()  # Держим соединение открытым

            if data.startswith("/binary_image"):
                image_data = data.split(maxsplit=1)[1]
                task = binarize_image.delay(image_data, client_id)

            elif data.startswith("/"):
                command = data[1:].split()[0]
                args = data[1:].split()[1:]

                try:
                    result = await execute_command(command, args)
                    await websocket.send_text(json.dumps({
                        'status': 'COMPLETED',
                        'command': command,
                        'result': result
                    }))
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        'status': 'FAILED',
                        'command': command,
                        'message': str(e)
                    }))

    except WebSocketDisconnect:
        listener.cancel()
        pubsub.close()


# @app.post("/process-image")
# async def process_image(data: dict):
#     task = binarize_image.delay(data['image_data'], str(data['client_id']))
#     return {"task_id": task.id}


app.include_router(router_users)
