from . import qtl
from .. import db
from models import Cluster
from app.tasks import say_hello

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