from celery import Celery

celery = Celery(__name__,
                backend='rpc://',
                broker="amqp://localhost"
)

@celery.task(name='app.tasks.say_hello')
def say_hello():
    return "Hello"