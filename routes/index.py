from flask import Blueprint, request, render_template
from navigator import navigator
from cookies import create_cookie

index_blueprint = Blueprint('index', __name__)

@index_blueprint.route('/')
@navigator
@create_cookie
def index():
    endpoint = 'index'
    return render_template(endpoint+'.jinja2', js_file='js/'+endpoint+'.js')

def register_routes(app):
    app.register_blueprint(index_blueprint)