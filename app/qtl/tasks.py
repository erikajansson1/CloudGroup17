from celery import Celery
import json
import time
from helpers import create_cluster, delete_cluster, scale_worker

celery = Celery(__name__,
                backend='rpc://',
                broker="pyamqp://myuser:mypassword@acc17-qts.duckdns.org/myvhost"
)

@celery.task(name='app.tasks.say_hello')
def say_hello():
    return "Hello"


@celery.task(name='app.tasks.celery_create_cluster')
def celery_create_cluster(user_id, number_of_workers):
    return create_cluster(user_id, number_of_workers)

@celery.task(name='app.tasks.celery_delete_cluster')
def celery_delete_cluster(user_id, cluster_id):
    return delete_cluster(user_id, cluster_id)

@celery.task(name='app.tasks.celery_scale_worker')
def celery_scale_worker(user_id, cluster_id, number_of_workers):
    return scale_worker(user_id, cluster_id, number_of_workers)