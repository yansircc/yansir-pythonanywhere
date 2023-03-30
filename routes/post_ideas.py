from flask import Blueprint, request, render_template, jsonify
from golem import Golem
import os
import re

post_ideas_blueprint = Blueprint('post_ideas', __name__)

@post_ideas_blueprint.route('/ideas')
def ideas():
    return render_template('post-ideas.html')

@post_ideas_blueprint.route('/post-ideas', methods=['POST'])
def post_ideas_endpoint():
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    data = request.get_json()
    keywords = data['keywords']
    processes = data['processes']
    mixed_list = []
    for keyword in keywords:
        for proc in processes:
            mixed_list.append(keyword + '+' + proc)
    mixed_strings = ', '.join(mixed_list)

    sys_prompt = data['trained_data']
    sys_prompt = re.sub(r"Based on the above information.*", "", sys_prompt)
    sys_prompt_prefix = "The following information is about you identity and your business. You will read it in the first person: "
    user_input_prefix = "From your angle of view, "
    user_input_suffix = " What are some B2B blog post ideas that you can come up with? Note that the post title should be a clickbait question. Output in this format: [English blog title: Chinese translation], and don't explain anything."
    post_ideas_golem = Golem(openai_api_key, sys_prompt, sys_prompt_prefix, user_input_prefix, user_input_suffix)

    user_input = mixed_strings
    response = post_ideas_golem.response(user_input)
    
    return jsonify({'response': response})


def register_routes(app):
    app.register_blueprint(post_ideas_blueprint)