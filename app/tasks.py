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


@celery.task(name='app.tasks.celery_create_cluster')
def celery_create_cluster(number_of_workers):
    time.sleep(30)
    return json.dumps({'success': True,
            'cluster_id': 1000,
            'jupyter_url': '<jupyter_url>'})

@celery.task(name='app.tasks.celery_delete_cluster')
def celery_delete_cluster(cluster_id):
    time.sleep(30)
    return json.dumps({'success': True})

@celery.task(name='app.tasks.celery_scale_worker')
def celery_scale_worker(cluster_id, number_of_workers):
    time.sleep(30)
    return json.dumps({'success': True})    