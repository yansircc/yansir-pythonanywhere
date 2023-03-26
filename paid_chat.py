from flask import Blueprint, request, render_template, jsonify
import openai

paid_chat_blueprint = Blueprint('paid_chat', __name__)

@paid_chat_blueprint.route('/chat')
def chat():
    return render_template('chat.html')

@paid_chat_blueprint.route('/chatgpt', methods=['POST'])
def chatgpt():
    chat_history = request.get_json()
    sys_prompt = "You're a man of few words."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{'role':"system", "content":sys_prompt}] + chat_history
    )
    chatgpt_response = response.choices[0].message['content']
    return jsonify({'response': chatgpt_response})

def register_routes(app):
    app.register_blueprint(paid_chat_blueprint)
