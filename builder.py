from flask import Blueprint, request, render_template, jsonify
import openai

builder_blueprint = Blueprint('builder', __name__)

@builder_blueprint.route('/builder')
def builder():
    return render_template('builder.html')

@builder_blueprint.route('/builder-submit', methods=['POST'])
def builder_submit():
    # System Prompts
    sys_prompt = """
    You are a programmer who helps me use a website builder that relies on JSON for front-end layout, and your task is to help me write code in JSON format.
    The following is important information.
    1. the JSON format for the user is {"type": "elementor", "elements":["nested here outter section"]};
    2. outter section with {"elType": "section", "isInner":false, "elements":["nested here column"]};
    3. column with {"elType": "column", "elements":["nested here widget or inner section"]};
    4. widget with {"elType": "widget", "widgetType": "here is the widget type"}, note that widget can only have "elType" and "widgetType" two keys and the corresponding value, absolutely can not have more keys;
    5. common widget types are: accordion, alert, counter, divider, google_maps, heading, icon, image, icon-box, icon-list, progress, social-icons, spacer, star-rating, tabs, testimonial, text-editor, toggle, video, animated-headline, blockquote, call-to-action, countdown, flip-box, form, gallery, hotspot, motion-fx, popup, pricing, progress-tracker, share-buttons, slides, social;
    6. Inner Section is similar to outter section except that the value of "isInner" is true;
    From now on, only formatted json code wrapped in three backticks should be output, and no need to explain what the code does.
    """

    # Retrieve user input from form
    prompt = request.form['query']

    # Extra additional prompt
    extra_prompt = "Your output must be written in English, code must be wrapped in three backticks."

    # Call OpenAI ChatGPT API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content":sys_prompt},{"role":"user","content":prompt + extra_prompt}]
    )

    # Extract the response text from the API response
    query = response.choices[0].message['content']
    return jsonify({'response': query})

def register_routes(app):
    app.register_blueprint(builder_blueprint)
