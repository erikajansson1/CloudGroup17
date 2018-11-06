from . import auth
from .. import db
from app.auth.models import User
from app.qtl.models import Cluster, VirtualMachine
from flask import render_template, request, session, redirect, url_for
import json
from helpers import *


@auth.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    message = User.create_user(username=username, email=email, password=password, confirm_passowrd=confirm_password)
    if message == "":
        return json.dumps({'success': True})
    else:
        return json.dumps({'success': False, 'message': message})

    
@auth.route('/signin', methods=['POST'])
def signin():
    username = request.form['username']
    password = request.form['password']
    user_id = verify_signin(username, password)
    if user_id is not None:
        return json.dumps({'success': True, 'token': generate_token(user_id)})
    else:
        return json.dumps({'success': False})


@auth.route("/verify-token", methods=['POST'])
def verify():
    token = request.headers['Authorization']
    if verify_token(token) is None:
        return json.dumps({'success': False})
    else:
        return json.dumps({'success': True})