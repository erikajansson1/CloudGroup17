# app/auth/helpers.py

import jwt
import app
from run import app
import datetime
from app.auth.models import User

def generate_token(userID):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=app.config['TOKEN_EXPIRED_PERIOD']),
        'iss': 'ACC17',
        'iat': datetime.datetime.utcnow(),
        'user_id': userID
    }
    
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except:
        return None
    return payload['user_id']
    # Signature has expired

def verify_signin(username, password):
    user = User.query.filter_by(username=username).first()
    if user is not None:
        if user.password == password:
            return user.id
    
    return None
