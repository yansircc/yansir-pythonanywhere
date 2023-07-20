from flask import Blueprint, request, render_template, Response, stream_with_context
from golem import Golem, openai_api_key, gpt4_api_key
from navigator import navigator
from cookies import create_cookie
from queue import Queue
import json

paid_chat_blueprint = Blueprint('paid_chat', __name__)
response_queue = Queue()

@paid_chat_blueprint.route('/paid-chat')
@navigator
@create_cookie
def paid_chat():
    form_data = [
        {'tag': 'textarea', 'name': 'user_input',
            'id': 'user_input', 'placeholder': '输入你的问题', 'rows': '5'},
        {'tag': 'input', 'type': 'submit', 'id': 'submit', 'value': '回车'}
    ]
    endpoint = request.path.lstrip('/')
    return render_template(endpoint+'.jinja2', js_file='js/'+endpoint+'.js', form_data=form_data)


@paid_chat_blueprint.route('/sse/paid_chat', methods=['GET','POST'])
def handle_user_input():
    if request.method == 'POST':
        user_input = request.form['user_input']
        chat_history = request.form['chat_history'] if 'chat_history' in request.form else None
        session_id = request.cookies.get('user_id')
        sys_prompt = "You're a man of few words."
        paid_golem = Golem(openai_api_key, session_id, sys_prompt=sys_prompt, is_gpt4=False)
        if chat_history:
            chat_rounds = json.loads(chat_history)
            transcript_history = []
            for round in chat_rounds:
                for key, value in round.items():
                    transcript_history.append({'role': 'user', 'content': key})
                    transcript_history.append({'role': 'assistant', 'content': value})
            transcript_history.append({'role': 'user', 'content': user_input})
            response = paid_golem.response(transcript_history)
        else:
            response = paid_golem.response(user_input)
        response_queue.put(response)
        return '', 204
    else:
        response = response_queue.get()
        return Response(stream_with_context(response), mimetype='text/event-stream')


def register_routes(app):
    app.register_blueprint(paid_chat_blueprint)
