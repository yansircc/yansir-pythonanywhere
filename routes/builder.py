from flask import Blueprint, request, render_template, Response, stream_with_context
from golem import Golem, openai_api_key
from navigator import navigator
from queue import Queue
from cookies import create_cookie

builder_blueprint = Blueprint('builder', __name__)
response_queue = Queue()


@builder_blueprint.route('/builder')
@navigator
@create_cookie
def builder():
    form_data = [
        {'tag': 'input', 'type': 'text', 'name': 'user_input', 'id': 'user_input', 'placeholder': '比如：我要一行两列，左边图右边标题+视频'},
        {'tag': 'input', 'type': 'submit', 'id': 'submit', 'value': '回车'}
    ]
    endpoint = request.path.lstrip('/')
    return render_template(endpoint+'.jinja2', js_file='js/'+endpoint+'.js', form_data=form_data)


@builder_blueprint.route('/builder_golem', methods=['GET', 'POST'])
def builder_golem():
    if request.method == 'POST':
        user_input = request.form['user_input']
        session_id = request.cookies.get('user_id')
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
        builder_golem = Golem(openai_api_key, session_id,
                            sys_prompt=sys_prompt, user_input_suffix=user_input_suffix)
        response = builder_golem.response(user_input)
        response_queue.put(response)
        return '', 204
    else:
        response = response_queue.get()
        return Response(stream_with_context(response), mimetype='text/event-stream')



def register_routes(app):
    app.register_blueprint(builder_blueprint)
