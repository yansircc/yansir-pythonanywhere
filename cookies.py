from flask import make_response, session
from functools import wraps
from uuid import uuid4

def create_cookie(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            session['user_id'] = str(uuid4())
            resp = make_response(f(*args, **kwargs))
            resp.set_cookie('user_id', session['user_id'].encode('utf-8'))
            return resp
        return f(*args, **kwargs)
    return decorated_function
