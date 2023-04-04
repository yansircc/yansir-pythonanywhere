from flask import Blueprint, request, render_template
import json
import os

gtm_json_blueprint = Blueprint('gtm_json', __name__)

@gtm_json_blueprint.route('/gtm-json', methods=['GET'])
def gtm_json():
    form_data = [
        {'label': 'GA4 ID:', 'tag': 'input', 'type': 'text', 'id': 'ga4_id', 'placeholder': 'G-xxxxxx'},
        {'label': 'GA4 API Key:', 'tag': 'input', 'type': 'text', 'id': 'ga4_api_key', 'placeholder': 'AIzaSyxxxxxx'},
        {'label': 'GAds ID:', 'tag': 'input', 'type': 'text', 'id': 'gads_id', 'placeholder': 'AW-xxxxxx'},
        {'label': 'GAds Label:', 'tag': 'input', 'type': 'text', 'id': 'gads_label', 'placeholder': 'xxxxxx'},
        {'label': 'OpenAI API Key:', 'tag': 'input', 'type': 'text', 'id': 'openai_api_key' , 'placeholder': 'sk-xxxxxx'},
        {'label': '训练AI的命令:', 'tag': 'textarea', 'id': 'sys_prompt', 'rows': '5', 'placeholder': '你想让AI按什么标准给询盘打分?'},
        {'tag': 'input', 'type': 'submit', 'value': '生成我的Json'}
    ]
    endpoint = request.path.lstrip('/')
    return render_template(endpoint+'.jinja2', js_file='js/'+endpoint+'.js', form_data=form_data)

@gtm_json_blueprint.route('/generate_json', methods=['POST'])
def generate_json():
    data = request.get_json()
    ga4_id = data.get('ga4_id')
    ga4_api_key = data.get('ga4_api_key')
    gads_id = data.get('gads_id')
    gads_label = data.get('gads_label')
    openai_api_key = data.get('openai_api_key')
    sys_prompt = data.get('sys_prompt')

    # Get the directory of the current Python script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Go one level up from the 'routes' directory
    parent_dir = os.path.dirname(current_dir)

    # Build the absolute path for the 'gtm.json' file
    gtm_json_path = os.path.join(parent_dir, 'resources', 'gtm.json')

    with open(gtm_json_path, 'r') as f:
        gtm_json = f.read()
        gtm_json = gtm_json.replace('ga4_id_replace', ga4_id)
        gtm_json = gtm_json.replace('ga4_api_key_replace', ga4_api_key)
        gtm_json = gtm_json.replace('gads_id_replace', gads_id)
        gtm_json = gtm_json.replace('gads_label_replace', gads_label)
        gtm_json = gtm_json.replace('openai_api_key_replace', openai_api_key)
        gtm_json = gtm_json.replace('sys_prompt_replace', sys_prompt)

    return json.dumps(gtm_json)


def register_routes(app):
    app.register_blueprint(gtm_json_blueprint)