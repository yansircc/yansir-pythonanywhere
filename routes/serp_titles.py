from flask import Blueprint, request, render_template, Response, stream_with_context
from golem import Golem, openai_api_key ,openai_4_api_key, api_base
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
        {'label': '关键词：', 'tag': 'textarea', 'id': 'query', 'name': 'query',
            'placeholder': '输入你的核心关键词，每个关键词占一行', 'rows': '5'},
        {'tag': 'input', 'type': 'submit', 'id': 'submit', 'value': '回车'}
    ]
    endpoint = request.path.lstrip('/')
    return render_template(endpoint+'.jinja2', js_file='js/'+endpoint+'.js', form_data=form_data)


@serp_titles_blueprint.route('/sse/serp_titles', methods=['GET', 'POST'])
def serp_titles_golem():
    if request.method == 'POST':
        queries = request.form['query'].splitlines()
        session_id = request.cookies.get('user_id')

        serp_titles_golem = None
        for i, query in enumerate(queries):
            serp_titles = '\n'.join(serp_scraper(query))
            sys_prompt = "As a top-notch SEO copywriter, your job is to help me write better blog posts. I will query in google, and show you a list of titles form the first page. you will analyze those titles and give me some recommandations in given format."
            user_input = f"I queried {query} and find that these titles are ranking: {serp_titles}. My question is: What's the search intent of this query? (like informational, transactional, etc.) What's the best post type for this query?(like listicle, roundup, etc.) What's the best title for this query if you want to rank #1 in google? Write down your answer in this format(note that keep my newline character):Orginal query: [original query]\nSearch Intent: [Search intent]\nRecommand Post type: [Post type]\nRecommand title: [Your winning title here]\nFor example:\nOrginal query: how to make money\nSearch Intent: Informational\nRecommand Post type: Listicle\nRecommand title: 10 Ways to Make Money Online" 
            user_input_suffix = "Keep in mind leave 2 empty lines at the very end and strictly output the content according to the specified format."
            serp_titles_golem = Golem(openai_4_api_key, session_id, sys_prompt=sys_prompt, user_input_suffix=user_input_suffix, api_base=api_base)
            no_stop_sign = not(i == len(queries) - 1)
            response = serp_titles_golem.response(user_input, no_stop=no_stop_sign)
            response_queue.put(response)
        return '', 204
    else:
        def generate():
            while not response_queue.empty():
                response = response_queue.get()
                yield from response
        return Response(stream_with_context(generate()), mimetype='text/event-stream')

def register_routes(app):
    app.register_blueprint(serp_titles_blueprint)


def serp_scraper(query):
    api_key = "c0ddd631-6758-4993-9fdd-354e4bc195e4"
    query = query.replace(' ', '+')
    domain = "google.com"
    country = "us"
    language = "en"
    result_format = "json"
    device = "mobile"
    page_size = 16
    search_url = f"https://api.spaceserp.com/google/search?apiKey={api_key}&q={query}&location=New+York+Mills%2CMinnesota%2CUnited+States&domain={domain}&gl={country}&hl={language}&resultFormat={result_format}&device={device}&pageSize={page_size}&pageNumber=1"
    
    print(f"正在查询{query}的数据")
    response = requests.get(search_url)
    response_json = response.json()
    titles = []
    for result in response_json['organic_results']:
        titles.append(result['title'])
    return titles
