from celery import Celery 

app = Celery(
    'video-generator',
    backend='redis://localhost',
    broker = 'redis://localhost',
    include=['app.tasks']
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_acks_late=True,
)