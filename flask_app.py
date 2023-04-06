from flask import Flask, redirect, session, make_response, g
from flask_cors import CORS
from flask_assets import Environment, Bundle
from uuid import uuid4
import os
import importlib
import redis


app = Flask(__name__)
redis_client = redis.Redis(host='localhost', port=6379, db=0)

@app.before_request
def create_cookie():
    if 'user_id' not in session:
        session['user_id'] = str(uuid4())
        resp = make_response()
        resp.set_cookie('user_id', session['user_id'].encode('utf-8'))


CORS(app)

assets = Environment(app)
scss_bundle = Bundle('scss/style.scss', filters='pyscss',
                     output='css/style.css')
assets.register('scss_all', scss_bundle)


def register_routes_by_name(app, route_names):
    for route_name in route_names:
        module = importlib.import_module(f'routes.{route_name}')
        register_route_func = getattr(module, 'register_routes')
        register_route_func(app)


route_names = [
    'index',
    'builder',
    'paid_chat',
    'business',
    'leads_value',
    'post_ideas',
    'generate_post',
    'gtm_json',
    'anki_cards',
    'clear_db'
]
register_routes_by_name(app, route_names)


app.secret_key = os.getenv('SESSION_SECRET')


if __name__ == '__main__':
    app.run()
