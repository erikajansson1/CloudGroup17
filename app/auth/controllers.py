from . import auth
from .. import db
from app.auth.models import User
from app.qtl.models import Cluster, VirtualMachine
from flask import render_template, request, session, redirect, url_for
import json
from helpers import *
import forms


@auth.route('/signup', methods=['GET','POST'])
def signup():
    # Check if logged in, and redirect to home page in such case
    if 'user_id' in session:
        return redirect(url_for('home'))

    form = SignupForm()

    if request.method == "POST":
        if form.validate() == False:
      # reload the signup.html page if any validation check fails
            return render_template('signup.html', form=form)
        else:     
            # message = User.create_user(username=username, email=email, password=password, confirm_passowrd=confirm_password)
            details = User.create_user(form.username.data, form.email.data, form.password.data, form.confirm_passowrd.data)
            # after a new user signs up, a new session is created.
            session['user_id'] = details[1].id 
            return redirect(url_for('home'))
    elif request.method == "GET":
        return render_template('signup.html', form=form)

    '''        
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    message = User.create_user(username=username, email=email, password=password, confirm_passowrd=confirm_password)

    if message == "":
        return json.dumps({'success': True})
    else:
        return json.dumps({'success': False, 'message': message})
    '''
    
@auth.route('/signin', methods=["GET", "POST"])
def signin():

    form = LoginForm()

    if request.method == "POST":
        if form.validate() == False:
            return render_template("login.html", form=form)
        else:
            # if the login form validates, the data is fetched from the login form
            username = form.username.data 
            password = form.password.data
            user_id = verify_signin(username, password) 
            if user_id is not None:
                session['user_id'] = user_id
                return redirect(url_for('home')) # and redirecting to the home page

    elif request.method == 'GET':
        if 'user_id' in session:
            # Instead the user is redirected to login page
            return redirect(url_for('home'))
        return render_template('login.html', form=form)
        
    '''
    username = request.form['username']
    password = request.form['password']
            
    if user_id is not None:
        return json.dumps({'success': True, 'token': generate_token(user_id)})
    else:
        return json.dumps({'success': False})
    '''

@auth.route("/verify-token", methods=['POST'])
def verify():
    token = request.headers['Authorization']
    if verify_token(token) is None:
        return json.dumps({'success': False})
    else:
        return json.dumps({'success': True})