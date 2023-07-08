from flask import Blueprint, request, render_template, Response, stream_with_context, jsonify
from golem import Golem, openai_api_key ,openai_4_api_key, api_base
from navigator import navigator
from cookies import create_cookie
from queue import Queue
from scraper import serp_scraper


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
        sys_prompt = "As an SEO expert, guide me to craft better content. I'll provide Google query results. Analyze them and suggest improvements in the given format."
        user_input = f"Given my Google query {query} and its first page results {serp_results}, identify the search intent in SERP. (informational, transactional, etc.), suggest the most suitable content format (blog post, video, QA page, etc.) and corresponding content type (listicle, roundup, etc.), provide a top-ranking page title and corresponding descriptions. Answer in the following format: Search Intent: [Search intent(and it's proportion)]\n Content Format: [Content format]\n Content type: [Content type]\n Recommended title: [Your title here]\n Description: [Your desc here]. For instance(the initial query: how to make money): Search Intent: Informational(6/10) | Transactional(4/10)\n Content Format: Blog post\n Content type: Listicle\n Recommended title: 10 Ways to Make Money Online\n Description: Here are 10 ways to make money online."
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

@serp_titles_blueprint.route('/no_sse/serp_titles', methods=['POST'])
def serp_titles_golem_no_sse():
    query = request.form['query']
    session_id = request.cookies.get('user_id')

    serp_titles_golem = None
    
    query_amount = 10
    serp_results = '\n'.join(serp_scraper(query, query_amount))
    sys_prompt = "As an SEO expert, guide me to craft better content. I'll provide Google query results. Analyze them and suggest improvements in the given format."
    user_input = f'Given my Google query {query} and its first {query_amount} results {serp_results} write down your insights in the following format: Search intent: [identify the search intent in SERP and provide the corresponding reliability score without any explaination. (informational, transactional, etc.)]\n Content format: [suggest the most suitable content format (blog post, video, QA page, etc.), just one]\n Content type: [corresponding content type (listicle, roundup, etc.), just one]\n Recommended title: [provide a top-ranking page title]\n Description: [corresponding description]. For instance(the initial query: long sleeve sun shirt): Search intent: Transactional with 90% reliability\n Content format: Product page\n Content type: Roundup\n Recommended title: Top 10 Long Sleeve Sun Shirts for Ultimate Protection\n Description: Explore our top picks for long sleeve sun shirts, offering the best in UV protection and comfort for all your outdoor adventures.'
    user_input_suffix = "Ensure your response strictly follows the above format."
    serp_titles_golem = Golem(openai_4_api_key, session_id, sys_prompt=sys_prompt, user_input_suffix=user_input_suffix, api_base=api_base, is_stream=False, temperature=0.1)

    response = serp_titles_golem.response(user_input)
    result = next(response)
    return jsonify(result)  # Return as JSON


def register_routes(app):
    app.register_blueprint(serp_titles_blueprint)
