from celery import Celery 

app = Celery(
    'app.celery_app',
    backend='redis://localhost',
    broker = 'redis://localhost',
)