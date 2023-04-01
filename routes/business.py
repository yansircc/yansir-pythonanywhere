from flask import Blueprint, request, render_template, jsonify
from golem import Golem, openai_api_key

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
    sys_prompt = "You are a successful Chinese business owner. Now, you have to describe your business to ChatGPT."
    user_input_prefix = "This is your business information: "
    user_input_suffix = "A key with the keyword 'PERSONAS' indicates that the value is information about your target audience, and a key with the keyword 'MY-BUSINESS' indicates that the value is information about your business. Now start your description in English."
    append_prompt = " Based on the above information execute my command: [PROMPT]. Note that you always have to write copy for my typical client, from his point of interest, and add value."
    business_golem = Golem(openai_api_key, sys_prompt=sys_prompt, user_input_prefix=user_input_prefix, user_input_suffix=user_input_suffix)

    user_input = request.form.get('prompt')
    response = business_golem.response(user_input)
    raw_trained_data = response
    response += append_prompt

    summary_golem = Golem(openai_api_key, sys_prompt=" You're a man of few word.", user_input_prefix="Summarize the following information into a paragraph of no more than 200 words: ", max_tokens=1000)
    summaried_trained_data = summary_golem.response(raw_trained_data)

    return jsonify({'response': response, 'summaried_trained_data': summaried_trained_data})


def register_routes(app):
    app.register_blueprint(business_blueprint)