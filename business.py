from flask import Blueprint, request, render_template, jsonify
import openai

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
    prefix_prompt = "This is your business information: "
    suffix_prompt = "A key with the keyword 'PERSONAS' indicates that the value is information about your target audience, and a key with the keyword 'MY-BUSINESS' indicates that the value is information about your business. Now start your description in English."
    append_prompt = " Based on the above information execute my command: [PROMPT]. Note that you always have to write copy for my typical client, from his point of interest, and add value."
    prompt = request.form.get('prompt')  # Get the text from the response container
    # Call the OpenAI API to train the model
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content":sys_prompt},{"role":"user","content":prefix_prompt + prompt + suffix_prompt}]
    )
    query = response.choices[0].message['content'] + append_prompt
    return jsonify({'response': query})

def register_routes(app):
    app.register_blueprint(business_blueprint)