from flask import Blueprint, request, render_template, jsonify
from golem import Golem, openai_api_key

builder_blueprint = Blueprint('builder', __name__)

@builder_blueprint.route('/builder')
def builder():
    return render_template('builder.html')

@builder_blueprint.route('/builder-submit', methods=['POST'])
def builder_submit():
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
    user_input_suffix = "Your output must be written in English, code must be wrapped in three backticks."
    builder_golem = Golem(openai_api_key,sys_prompt=sys_prompt, user_input_suffix=user_input_suffix)

    user_input = request.form['query']
    response = builder_golem.response(user_input)

    return jsonify({'response': response})


def register_routes(app):
    app.register_blueprint(builder_blueprint)
