from flask import Blueprint, request, render_template, jsonify
from golem import Golem, openai_api_key

anki_cards_blueprint = Blueprint('anki_cards', __name__)

@anki_cards_blueprint.route('/anki-cards')
def anki_cards():
    return render_template('anki-cards.html')

@anki_cards_blueprint.route('/generate_anki_cards', methods=['POST'])
def generate_anki_cards():
    data = request.get_json()
    user_input = data['user_input']
    sys_prompt = "generate anki cards and output in json format"

    anki_cards_golem = Golem(openai_api_key, sys_prompt=sys_prompt)
    response = anki_cards_golem.response(user_input)
    #处理response，确保只有Json格式的文本
    
    return jsonify({'response': response})

def register_routes(app):
    app.register_blueprint(anki_cards_blueprint)