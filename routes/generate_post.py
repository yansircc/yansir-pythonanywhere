from flask import Blueprint, request, render_template
from golem import Golem, openai_api_key
from transcripts_db import TranscriptsDB
from navigator import navigator
import re


generate_post_blueprint = Blueprint('generate_post', __name__)

@generate_post_blueprint.route('/generate-post', methods=['GET'])
@navigator
def generate_post():
    form_data = [
        {'tag': 'input', 'type': 'text', 'name': 'user_input', 'id': 'user_input', 'placeholder': '输入英文标题'},
        {'tag': 'input', 'type': 'submit', 'id': 'submit', 'value': '回车'}
    ]
    endpoint = request.path.lstrip('/')
    return render_template(endpoint+'.jinja2', js_file='js/'+endpoint+'.js', form_data=form_data)

@generate_post_blueprint.route('/generate_post', methods=['GET'])
def generate_post_golem():
    session_id = request.args.get('session_id')
    user_input = request.args.get('user_input')
    post_type = request.args.get('post_type')
    title = ' '.join(re.findall(r'[a-zA-Z\s]+', user_input))
    
    generate_post_db = TranscriptsDB()
    with generate_post_db as db:
        business_prompts = db.retrieve_data('conversation', session_id, 'business_prompts')

    if business_prompts:
        sys_prompt = "The following information is about you identity and your business. You will read it in the first person: " + business_prompts

        if post_type == 'response_post':
            max_word_count = 1200
            response_post_golem = Golem(openai_api_key, session_id, sys_prompt=sys_prompt, max_tokens=500)
            user_input = f'''
            From you angle of view, Write a blog post(between {max_word_count-100} to {max_word_count+100} words) about {title}. 
            Keep in mind that you need to:
            1. Inset a resources link for those keywords which need data support;
            2. Short sentence, split the paragraph more often;
            3. Output in English and html format;
            Here is a example of what you should do:
            <h1>A title end with question mark?</h1>
            <p>Frist paragraph, multiple rhetorical questions or a fabricated story.(80 words)</p>
            <p><strong>Second paragraph, provide a brief and helpful answer to the title.(80 words)</strong></p>
            <p>Maintaining readers' interest in continuing to read.(30 words)</p>
            <h2>Topic related question end with question mark?</h2>
            <p>Bold all keywords which need data support.</p>
            <h2>More related questions</h2>
            <p>answers</p>
            ...
            <h2>Conclusion</h2>
            <p>Within 50 words.</p>
            '''
            response = response_post_golem.response(user_input)
            
        elif post_type == 'listicle':
            pass
        elif post_type == 'pillar_post':
            pass
        else:
            post_ideas_golem = Golem(openai_api_key, session_id, sys_prompt="Don't output anything but '文章类型错误。'.")
            response = post_ideas_golem.response("Output the error message.")
    else:
        post_ideas_golem = Golem(
            openai_api_key, session_id, sys_prompt="Don't output anything but '数据缺失，请先完成预训练。'.")
        response = post_ideas_golem.response("Output the error message.")

    return response

def register_routes(app):
    app.register_blueprint(generate_post_blueprint)