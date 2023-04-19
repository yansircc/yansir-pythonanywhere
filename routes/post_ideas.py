from flask import Blueprint, request, render_template, Response, stream_with_context
from golem import Golem, openai_api_key
# from transcripts_db import TranscriptsDB
from navigator import navigator
from cookies import create_cookie
from queue import Queue


post_ideas_blueprint = Blueprint('post_ideas', __name__)
response_queue = Queue()


@post_ideas_blueprint.route('/post-ideas')
@navigator
@create_cookie
def post_ideas():
    form_data = [
        {'label': '关键词：', 'tag': 'textarea', 'id': 'keyword', 'name': 'keyword',
            'placeholder': '输入你的核心关键词，每个关键词占一行', 'rows': '5'},
        {'label': '流程：', 'tag': 'textarea', 'id': 'process', 'name': 'process',
            'placeholder': '输入行业关键流程，每个流程占一行', 'rows': '5'},
        {'tag': 'input', 'type': 'submit', 'id': 'submit', 'value': '回车'}
    ]
    endpoint = request.path.lstrip('/')
    return render_template(endpoint+'.jinja2', js_file='js/'+endpoint+'.js', form_data=form_data)


@post_ideas_blueprint.route('/sse/post_ideas', methods=['GET', 'POST'])
def post_ideas_golem():
    if request.method == 'POST':
        keyword = request.form['keyword']
        process = request.form['process']
        business_prompts = request.form['businessPrompt']
        session_id = request.cookies.get('user_id')
        mixed_strings = process_data(keyword, process)

        # post_ideas_db = TranscriptsDB()
        # with post_ideas_db as db:
        #     business_prompts = db.retrieve_data(
        #         'conversation', session_id, 'business_prompts')
        if business_prompts:
            sys_prompt = business_prompts[:business_prompts.rfind('\n')] # remove the last line
            sys_prompt_prefix = "The following information is about you identity and your business. You will read it in the first person: "
            user_input_prefix = "From your angle of view, "
            user_input_suffix = " What are some B2B blog post ideas that you can come up with? Note that the post title should be a clickbait question. Output in this format: English blog title[Chinese translation], and don't explain anything."
            post_ideas_golem = Golem(openai_api_key, session_id, sys_prompt=sys_prompt, sys_prompt_prefix=sys_prompt_prefix,
                                     user_input_prefix=user_input_prefix, user_input_suffix=user_input_suffix)
        else:
            post_ideas_golem = Golem(
                openai_api_key, session_id, sys_prompt="Don't output anything but '数据缺失，请先完成预训练。'.")

        response = post_ideas_golem.response(mixed_strings)
        response_queue.put(response)
        return '', 204
    else:
        response = response_queue.get()
        return Response(stream_with_context(response), mimetype='text/event-stream')


def process_data(keyword, process):
    keyword = keyword.split('\n')
    process = process.split('\n')
    result = ','.join([k+'+'+p for k in keyword for p in process])
    return (result)


def register_routes(app):
    app.register_blueprint(post_ideas_blueprint)