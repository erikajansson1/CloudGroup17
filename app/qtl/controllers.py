from . import qtl
from .. import db
from models import Cluster
from app.tasks import say_hello, celery_create_cluster
from app import celery_task_results
from flask import request, url_for
from app.auth.helpers import verify_token
import json

# @qtl.route('/cluster/create')
# def say_hello():
#     cluster = Cluster(jupyter_url='xxx')
#     db.session.add(cluster)
#     db.session.commit()

#     return "Hello"


@qtl.route("/celery/test")
def say():
    result = say_hello.delay()
    return result.get()


@qtl.route("/cluster/create", methods=['POST'])
def create_cluster():
    response_data = {}
    token = request.headers['Authorization']
    user_id = verify_token(token)
    
    if user_id is None:
        response_data['verify-token'] = False
    else:
        response_data['verify-token'] = True
        number_of_workers = request.form['number_of_workers']
        try:
            task = celery_create_cluster.delay(number_of_workers)
            response_data['task_id'] = task.id
            response_data['success'] = True
        except:
            response_data['success'] = False
            response_data['message'] = ""

    return json.dumps(response_data), 202, {'Location': url_for('qtl.tasks_result',
                                                  task_id=task.id)}


@qtl.route('/cluster/create/status/<task_id>', methods=['GET'])
def tasks_result(task_id):
    response_data = {}
    token = request.headers['Authorization']
    user_id = verify_token(token)
    
    if user_id is None:
        response_data['verify-token'] = False
    else:
        response_data['verify-token'] = True
        task = celery_create_cluster.AsyncResult(task_id)

        if task_id in celery_task_results:
            response_data['state'] = task.state
            response_data['result'] = celery_task_results[task.id]
        else:
            if task.state == 'PENDING':
                # job did not start yet
                response_data['state'] = task.state
            elif task.state != 'FAILURE':
                celery_task_results[task.id] = task.get()
                response_data['state'] = task.state
                response_data['result'] = celery_task_results[task.id]
            else:
                # something went wrong in the background job
                response_data['state'] = task.state
                response_data['status'] = str(task.info)

    return json.dumps(response_data)