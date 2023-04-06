from flask_app import app
from dotenv import load_dotenv
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple


load_dotenv()
application = app.wsgi_app

if __name__ == '__main__':
    run_simple('localhost', 5000, application)
