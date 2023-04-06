from flask import Flask
from flask_cors import CORS
from flask_assets import Environment, Bundle
import os
import importlib
from dotenv import load_dotenv


load_dotenv(".env")
app = Flask(__name__)
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
