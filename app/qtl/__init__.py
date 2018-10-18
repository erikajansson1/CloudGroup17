# app/auth/__init__.py

from flask import Blueprint

qtl = Blueprint('qtl', __name__)

from . import controllers