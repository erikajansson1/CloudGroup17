from celery import Celery
import json
import time

celery = Celery(__name__,
                backend='rpc://',
                broker="amqp://localhost"
)

@celery.task(name='app.tasks.say_hello')
def say_hello():
    return "Hello"


@celery.task(name='app.tasks.create_cluster')
def celery_create_cluster(number_of_workers):
    time.sleep(30)
    return json.dumps({'success': True,
            'cluster_id': 1000,
            'jupyter_url': '<jupyter_url>'})