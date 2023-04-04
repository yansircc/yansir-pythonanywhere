from flask import Blueprint, request, render_template
from navigator import navigator

index_blueprint = Blueprint('index', __name__)

@index_blueprint.route('/index')
@navigator
def index():
    endpoint = request.path.lstrip('/')
    return render_template(endpoint+'.jinja2', js_file='js/'+endpoint+'.js')

def register_routes(app):
    app.register_blueprint(index_blueprint)