from flask import Blueprint

api_bp = Blueprint('api', __name__)

from app.api import consumption, channel, main_type, sub_type, statistics
