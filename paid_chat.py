from flask import Blueprint, request, render_template, jsonify, session
from golem import Golem
import os

paid_chat_blueprint = Blueprint('paid_chat', __name__)

@paid_chat_blueprint.route('/chat')
def chat():
    session.clear()
    return render_template('chat.html')

@paid_chat_blueprint.route('/chatgpt', methods=['POST'])
def paid_golem():
    data = request.get_json()
    user_input = data['user_input']
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    sys_prompt = "You're a man of few words."
    paid_golem = Golem(openai_api_key, sys_prompt, memory=True)
    response = paid_golem.response(user_input)
    return jsonify({'response': response})


def register_routes(app):
    app.register_blueprint(paid_chat_blueprint)
