from flask import Blueprint, request, render_template, Response, stream_with_context
from golem import Golem, openai_api_key ,openai_4_api_key, api_base
from navigator import navigator
from cookies import create_cookie
from queue import Queue
import requests
from client import RestClient
import os


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
        query = request.form['query']
        session_id = request.cookies.get('user_id')

        serp_titles_golem = None
        
        serp_results = '\n'.join(serp_scraper(query))
        sys_prompt = "As an SEO copywriting expert, guide me to craft better content. I'll provide Google query results as titles. Analyze these and suggest improvements in the given format."
        user_input = f"Given my Google query {query} and its first page results {serp_results}, identify the search intent with the highest proportion in SERP. (informational, transactional, etc.), suggest the most suitable content format (blog post, video, QA page, etc.) and corresponding content type (listicle, roundup, etc.), provide a top-ranking title and corresponding descriptions. Answer in the following format: Search Intent: [Search intent(and it's proportion)]\n Content Format: [Content format]\n Content type: [Content type]\n Recommended title: [Your title here]\n Description: [Your desc here]. For instance(the initial query: how to make money): Search Intent: Informational(6/10)\n Content Format: Blog post\n Content type: Listicle\n Recommended title: 10 Ways to Make Money Online\n Description: Here are 10 ways to make money online."
        user_input_suffix = "Ensure your response strictly follows the above format."
        serp_titles_golem = Golem(openai_4_api_key, session_id, sys_prompt=sys_prompt, user_input_suffix=user_input_suffix, api_base=api_base)
        
        response = serp_titles_golem.response(user_input)
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
    client = RestClient(os.getenv("DFS_ADMIN_EMAIL"), os.getenv("DFS_API_KEY"))
    post_data = dict()
    # You can set only one task at a time
    post_data[len(post_data)] = dict(
        language_code="en",
        location_name="New York Mills,Minnesota,United States",
        keyword=query,
        device="mobile",
        os="ios",
        depth=10,
        max_crawl_pages=1,
    )
    response = client.post("/v3/serp/google/organic/live/regular", post_data)
    # you can find the full list of the response codes here https://docs.dataforseo.com/v3/appendix/errors
    if response["status_code"] == 20000:
        items = response["tasks"][0]["result"][0]["items"]
        titles = []
        # featured_snippet = None
        for item in items:
            if item["type"] == "organic":
                titles.append(f'[rank: {item["rank_group"]}, title: {item["title"]}, desc: {item["description"]}]')
            if item["type"] == "featured_snippet":
                pass
        return titles
    else:
        print("error. Code: %d Message: %s" % (response["status_code"], response["status_message"]))
