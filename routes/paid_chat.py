from flask import Blueprint, request, render_template, session
from golem import Golem, openai_api_key


paid_chat_blueprint = Blueprint('paid_chat', __name__)

@paid_chat_blueprint.route('/paid-chat')
def paid_chat():
    return render_template('paid-chat.html')

@paid_chat_blueprint.route('/paid_chat', methods=['GET'])
def paid_golem():

    user_input = request.args.get('user_input', '')
    session_id = request.args.get('session_id', '')
    sys_prompt = "You're a man of few words."
    paid_golem = Golem(openai_api_key, session_id, sys_prompt=sys_prompt, memory=True)

    return paid_golem.response(user_input)

def register_routes(app):
    app.register_blueprint(paid_chat_blueprint)
