from flask import Blueprint, request, render_template
from golem import Golem, openai_api_key
from navigator import navigator


paid_chat_blueprint = Blueprint('paid_chat', __name__)


@paid_chat_blueprint.route('/paid-chat')
@navigator
def paid_chat():
    form_data = [
        {'tag': 'input', 'type': 'text', 'name': 'user_input', 'id': 'user_input', 'placeholder': '输入你的问题'},
        {'tag': 'input', 'type': 'submit', 'id': 'submit', 'value': '回车'}
    ]
    endpoint = request.path.lstrip('/')
    return render_template(endpoint+'.jinja2', js_file='js/'+endpoint+'.js', form_data=form_data)


@paid_chat_blueprint.route('/paid_chat', methods=['GET'])
def paid_golem():
    session_id = request.args.get('session_id', '')
    sys_prompt = "You're a man of few words."
    paid_golem = Golem(openai_api_key, session_id,
                       sys_prompt=sys_prompt, memory=True, table_name='conversation', column_name='transcript_history')
    user_input = request.args.get('user_input', '')
    return paid_golem.response(user_input)


def register_routes(app):
    app.register_blueprint(paid_chat_blueprint)
