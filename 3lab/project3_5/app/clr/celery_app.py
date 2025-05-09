import sys
from os.path import dirname, abspath
sys.path.insert(0, dirname(dirname(abspath(__file__))))

from celery import Celery
import redis
from serv.image_bin import all_the_bradley
import json
import time

app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json'
)

redis_conn = redis.StrictRedis()


@app.task(bind=True, name='clr.celery_app.test_task')
def binarize_image(self, image_data: str, client_id: str):
    task_id = self.request.id  # Отправляем уведомление о начале обработки

    def notify(status, **kwargs):  # Уведомление о начале
        redis_conn.publish(f'ws_{client_id}', json.dumps({
            'status': status,
            'task_id': task_id,
            **kwargs
        }))

    notify('STARTED', algorithm='Bradley')

    for progress in [25, 50, 75, 100]:
        notify('PROGRESS', progress=progress)
        time.sleep(0.3)

    result = all_the_bradley(image_data)  # Уведомление о завершении
    notify('COMPLETED', binarized_image=result)

    return result
