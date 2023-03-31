from flask import Blueprint, request, render_template, jsonify
from golem import Golem, openai_api_key

paid_chat_blueprint = Blueprint('paid_chat', __name__)

@paid_chat_blueprint.route('/paid-chat')
def paid_chat():
    return render_template('paid_chat.html')

@paid_chat_blueprint.route('/paid-chat', methods=['POST'])
def paid_golem():
    data = request.get_json()
    user_input = data['user_input']
    sys_prompt = "You're a man of few words."
    paid_golem = Golem(openai_api_key, sys_prompt=sys_prompt, memory=True)
    response = paid_golem.response(user_input)
    return jsonify({'response': response})


def register_routes(app):
    app.register_blueprint(paid_chat_blueprint)
