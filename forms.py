from flask_wtf import Form 
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

# Validators from Flask WTF
# Validators: # The validation check will return true if all the requirements are met else false
# - Data Required checks that none of the fields are empty in the form
# - Length of the password
# - The email address is valid
class SignupForm(Form): # This class inherits from Form class in Flask-WTF
  username = StringField('Username', validators=[DataRequired("Please enter a username.")])
  email = StringField('Email', validators=[DataRequired("Please enter your email address."), Email("Please enter a valid email address.")])
  password = PasswordField('Password', validators=[DataRequired("Please enter a password."), Length(min=6, message="Passwords must be 6 characters or more.")])
  confirm_password = PasswordField('Password', validators=[DataRequired("Please enter a password."), Length(min=6, message="Passwords must be 6 characters or more.")])
  submit = SubmitField('Sign up')

class LoginForm(Form):
  email = StringField('Email', validators=[DataRequired("Please enter your email address."), Email("Please enter a valid email address.")])
  password = PasswordField('Password', validators=[DataRequired("Please enter a password.")])
  submit = SubmitField("Sign in")