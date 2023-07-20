from flask import Flask, Blueprint, request, render_template, stream_with_context, send_file, Response
from golem import Golem, openai_api_key
from navigator import navigator
from cookies import create_cookie
from queue import Queue
from xmlrpc import client as xmlrpc_client
from wordpress_xmlrpc.methods import media
from wordpress_xmlrpc import Client, WordPressPost
import json
from PIL import Image
import requests
from io import BytesIO
from werkzeug.utils import secure_filename
import os
import re
import threading
from midjourney_api import TNL
import time

cors_proxy_blueprint = Blueprint('cors_proxy', __name__)
response_queue = Queue()
# NextLeg API
token = os.getenv("NEXT_LEG_TOKEN")
tnl = TNL(token)

@cors_proxy_blueprint.route('/cors-proxy')
@navigator
@create_cookie
def cors_proxy():
    form_data = [
        {'tag': 'input', 'type': 'submit', 'id': 'submit', 'value': '提交文档'}
    ]
    endpoint = request.path.lstrip('/')
    return render_template(endpoint+'.jinja2', js_file='js/'+endpoint+'.js', form_data=form_data)

def register_routes(app):
    app.register_blueprint(cors_proxy_blueprint)