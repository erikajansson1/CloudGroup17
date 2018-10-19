# run.py

import os
from app.models import User
from app import create_app, db

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)
app.app_context().push()
db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
