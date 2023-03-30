from flask import Blueprint, request, render_template, jsonify
from golem import Golem
import os

business_blueprint = Blueprint('business', __name__)

@business_blueprint.route('/business')
def business():
    return render_template('business.html')

@business_blueprint.route('/submit-business-form', methods=['POST'])
def submit_business_form():
    data = request.form.to_dict()
    return jsonify(data)

@business_blueprint.route('/chatgpt-training', methods=['POST'])
def chatgpt_training():
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    sys_prompt = "You are a successful Chinese business owner. Now, you have to describe your business to ChatGPT."
    user_input_prefix = "This is your business information: "
    user_input_suffix = "A key with the keyword 'PERSONAS' indicates that the value is information about your target audience, and a key with the keyword 'MY-BUSINESS' indicates that the value is information about your business. Now start your description in English."
    append_prompt = " Based on the above information execute my command: [PROMPT]. Note that you always have to write copy for my typical client, from his point of interest, and add value."
    business_golem = Golem(openai_api_key, sys_prompt, user_input_prefix, user_input_suffix)

    user_input = request.form.get('prompt')
    response = business_golem.response(user_input)
    response += append_prompt

    return jsonify({'response': response})


def register_routes(app):
    app.register_blueprint(business_blueprint)