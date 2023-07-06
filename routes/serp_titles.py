from flask import Blueprint, request, render_template, Response, stream_with_context
from golem import Golem, openai_api_key ,openai_4_api_key
from navigator import navigator
from cookies import create_cookie
from queue import Queue
import requests


serp_titles_blueprint = Blueprint('serp_titles', __name__)
response_queue = Queue()


@serp_titles_blueprint.route('/serp-titles')
@navigator
@create_cookie
def serp_titles():
    form_data = [
        {'label': '关键词：', 'tag': 'textarea', 'id': 'keyword', 'name': 'keyword',
            'placeholder': '输入你的核心关键词，每个关键词占一行', 'rows': '5'},
        {'tag': 'input', 'type': 'submit', 'id': 'submit', 'value': '回车'}
    ]
    endpoint = request.path.lstrip('/')
    return render_template(endpoint+'.jinja2', js_file='js/'+endpoint+'.js', form_data=form_data)


@serp_titles_blueprint.route('/sse/serp_titles', methods=['GET', 'POST'])
def serp_titles_golem():
    if request.method == 'POST':
        keyword = request.form['keyword']
        session_id = request.cookies.get('user_id')
        serp_titles = '\n'.join(serp_scraper(keyword))
        sys_prompt = serp_titles + ". Output in this format:[post type] Blog title. For example: [Listicle] 10 Best SEO Tools for 2021."
        sys_prompt_prefix = "You are a top-notch SEO copywriter. You can imitate the titles on Google's first page and analyze the types of articles(such as listicles, roundups, How-to Post, Case Study, etc.), then write similar high-click-through-rate titles that can ranke #1. Now, analyze the following title from Google's first page and provide just one title which has the highest posibility to rank #1: "
        serp_titles_golem = Golem(openai_api_key, session_id, sys_prompt=sys_prompt, sys_prompt_prefix=sys_prompt_prefix)

        response = serp_titles_golem.response(keyword)
        response_queue.put(response)
        return '', 204
    else:
        response = response_queue.get()
        return Response(stream_with_context(response), mimetype='text/event-stream')


def register_routes(app):
    app.register_blueprint(serp_titles_blueprint)


def serp_scraper(keywords):
    api_key = "c0ddd631-6758-4993-9fdd-354e4bc195e4"
    keywords = keywords.replace(' ', '+')
    search_url = f"https://api.spaceserp.com/google/search?apiKey={api_key}&q={keywords}&location=New+York+Mills%2CMinnesota%2CUnited+States&domain=google.com&gl=us&hl=en&resultFormat=json&device=mobile&mobileOs=ios&pageSize=10&pageNumber=1"
    response = requests.get(search_url)
    response_json = response.json()
    titles = []
    for result in response_json['organic_results']:
        titles.append(result['title'])
    return titles
