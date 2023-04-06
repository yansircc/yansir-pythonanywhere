from flask import Blueprint, request, render_template, Response, stream_with_context
from golem import Golem, openai_api_key
from transcripts_db import TranscriptsDB
from navigator import navigator
from queue import Queue
import re


generate_post_blueprint = Blueprint('generate_post', __name__)
response_queue = Queue()

@generate_post_blueprint.route('/generate-post', methods=['GET'])
@navigator
def generate_post():
    form_data = [
        {'tag': 'input', 'type': 'text', 'name': 'user_input', 'id': 'user_input', 'placeholder': '输入英文标题'},
        {'tag': 'input', 'type': 'submit', 'id': 'submit', 'value': '回车'}
    ]
    endpoint = request.path.lstrip('/')
    return render_template(endpoint+'.jinja2', js_file='js/'+endpoint+'.js', form_data=form_data)

@generate_post_blueprint.route('/generate_post', methods=['GET','POST'])
def generate_post_golem():
    if request.method == 'POST':
        session_id = request.cookies.get('user_id')
        title = ' '.join(re.findall(r'[a-zA-Z\s]+', request.form['user_input']))
        post_type = request.form['post_type']
        
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
                Here is a example of what you should do:
                # A title end with question mark?
                Frist paragraph, multiple rhetorical questions or a fabricated story.(80 words)
                **Second paragraph, provide a brief and helpful answer to the title.(80 words)**
                Maintaining readers' interest in continuing to read.(30 words)
                ## Topic related question end with question mark?
                Bold all keywords which need data support.
                ## More related questions
                answers
                more...
                ## Conclusion
                Within 50 words.
                That's it, output in English and markdown format.
                '''
            elif post_type == 'listicle':
                pass
            elif post_type == 'pillar_post':
                pass

            response = response_post_golem.response(user_input)
            
        else:
            post_ideas_golem = Golem(
                openai_api_key, session_id, sys_prompt="Don't output anything but '数据缺失，请先完成预训练。'.")
            response = post_ideas_golem.response("Output the error message.")

        response_queue.put(response)
        return '', 204
    else:
        response = response_queue.get()
        return Response(stream_with_context(response), mimetype='text/event-stream')

def register_routes(app):
    app.register_blueprint(generate_post_blueprint)