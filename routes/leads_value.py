from flask import Blueprint, request, jsonify
from flask_cors import CORS
from golem import Golem, openai_api_key

leads_value_blueprint = Blueprint('leads-value', __name__)

CORS(leads_value_blueprint, origins=["*"])

@leads_value_blueprint.route('/leads-value', methods=['POST'])
def leads_value():
    data = request.get_json()
    sys_prompt = data['sys_prompt']
    sys_prompt_prefix = "You're a rating machine. You will rate the inquiries on a scale of 0-100. "
    sys_prompt_suffix = " You always output score first head and then explain the reasons(within 100 words)."
    leads_check_golem = Golem(openai_api_key, sys_prompt=sys_prompt, sys_prompt_prefix=sys_prompt_prefix, sys_prompt_suffix=sys_prompt_suffix, temperature=0.2)

    user_input = data['leads_content']
    response = leads_check_golem(user_input)

    return jsonify({'response': response})


def register_routes(app):
    app.register_blueprint(leads_value_blueprint)