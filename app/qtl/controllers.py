from . import qtl
from .. import db
from app.qtl.models import Cluster, CeleryTask
from app.tasks import say_hello, celery_create_cluster, celery_delete_cluster, celery_scale_worker
from flask import request, url_for, redirect
from app.auth.helpers import verify_token
from app.auth.models import User
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
            user = User.query.filter_by(id=user_id).first()
            celery_task = CeleryTask(id=task.id, task_type='create_cluster', result=None)
            user.celery_tasks.append(celery_task)
            db.session.commit()
            response_data['task_id'] = task.id
            response_data['success'] = True
        except Exception as e:
            response_data['success'] = False
            response_data['message'] = e.message

    return json.dumps(response_data), 202, {'Location': url_for('qtl.tasks_result',
                                                  task_id=task.id)}

@qtl.route("/cluster/delete", methods=['POST'])
def delete_cluster():
    response_data = {}
    token = request.headers['Authorization']
    user_id = verify_token(token)
    
    if user_id is None:
        response_data['verify-token'] = False
    else:
        cluster_id = request.form['cluster_id']
        response_data['verify-token'] = True
        try:
            task = celery_delete_cluster.delay(cluster_id)
            user = User.query.filter_by(id=user_id).first()
            celery_task = CeleryTask(id=task.id, task_type='delete_cluster', result=None)
            user.celery_tasks.append(celery_task)
            db.session.commit()
            response_data['task_id'] = task.id
            response_data['success'] = True
        except Exception as e:
            response_data['success'] = False
            response_data['message'] = e.message

    return json.dumps(response_data), 202, {'Location': url_for('qtl.tasks_result',
                                                  task_id=task.id)}

@qtl.route("/worker/scale", methods=['POST'])
def scale_worker():
    response_data = {}
    token = request.headers['Authorization']
    user_id = verify_token(token)
    
    if user_id is None:
        response_data['verify-token'] = False
    else:
        cluster_id = request.form['cluster_id']
        number_of_workers = request.form['number_of_workers']
        response_data['verify-token'] = True
        try:
            task = celery_scale_worker.delay(cluster_id, number_of_workers)
            user = User.query.filter_by(id=user_id).first()
            celery_task = CeleryTask(id=task.id, task_type='delete_cluster', result=None)
            user.celery_tasks.append(celery_task)
            db.session.commit()
            response_data['task_id'] = task.id
            response_data['success'] = True
        except Exception as e:
            response_data['success'] = False
            response_data['message'] = e.message

    return json.dumps(response_data), 202, {'Location': url_for('qtl.tasks_result',
                                                  task_id=task.id)}

@qtl.route('/cluster/create/status/<task_id>', methods=['GET'])
@qtl.route('/cluster/delete/status/<task_id>', methods=['GET'])
@qtl.route('/worker/scale/status/<task_id>', methods=['GET'])
def tasks_result(task_id):
    return redirect(url_for('qtl.task_status', task_id=task_id))

@qtl.route('/task/<task_id>', methods=['GET'])
def task_status(task_id):
    response_data = {}
    token = request.headers['Authorization']
    user_id = verify_token(token)
    
    if user_id is None:
        response_data['verify-token'] = False
    else:
        response_data['verify-token'] = True
        task = celery_create_cluster.AsyncResult(task_id)
        task_db = CeleryTask.query.filter_by(id=task_id).first()
        print task.state
        if task_db is None:
            response_data['success'] = False
            response_data['message'] = 'task_id is invalid'
        else:
            response_data['success'] = True
            
            if task_db.result is not None:
                response_data['state'] = task.state
                response_data['result'] = json.loads(task_db.result)
            else:
                if task.state == 'PENDING':
                    # job did not start yet
                    response_data['state'] = task.state
                elif task.state != 'FAILURE':
                    task_db.result = task.get()
                    db.session.commit()
                    response_data['state'] = task.state
                    response_data['result'] = json.loads(task_db.result)
                else:
                    # something went wrong in the background job
                    response_data['state'] = task.state
                    response_data['status'] = str(task.info)

    return json.dumps(response_data)

