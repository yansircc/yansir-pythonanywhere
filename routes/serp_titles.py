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
        print("成功读取关键词：", queries)

        session_id = request.cookies.get('user_id')
        print("成功读取session_id")

        serp_titles_golem = None
        for i, query in enumerate(queries):
            serp_titles = '\n'.join(serp_scraper(query))
            sys_prompt = serp_titles + f"Now, analyze the following titles: {serp_titles}. Note that leave '\n---\n' at the end of your results."
            sys_prompt_prefix = '''
            As a top-notch SEO copywriter, you can analyze titles on Google's first page and find out the search intent behind the query, and write high-click-through-rate titles to rank #1. You will show your work in given format. For example:
            Query: SEO tips
            Search Intent: The user is looking for advice, strategies, or best practices to improve SEO(Translate this line into Chinese)
            Recommand Post type: Listicle
            Recommand title: 10 Best SEO Tools for 2021
            '''
            if not serp_titles_golem:
                serp_titles_golem = Golem(openai_api_key, session_id, sys_prompt=sys_prompt, sys_prompt_prefix=sys_prompt_prefix)
            else:
                serp_titles_golem.update_sys_prompt(sys_prompt)
            is_final = i == len(queries) - 1
            response = serp_titles_golem.response(query, is_final=is_final, is_multi=True)
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
