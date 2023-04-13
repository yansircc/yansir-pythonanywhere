from flask import Blueprint, request, render_template, jsonify
from navigator import navigator
from cookies import create_cookie
import os
import json

gtm_json_blueprint = Blueprint('gtm_json', __name__)


@gtm_json_blueprint.route('/gtm-json', methods=['GET'])
@navigator
@create_cookie
def gtm_json():
    form_data = [
        {'label': 'GA4 ID:', 'tag': 'input', 'type': 'text', 'required': True,
            'id': 'ga4_id', 'name': 'ga4_id', 'placeholder': 'G-xxxxxx'},
        {'label': 'Google Optimize ID:', 'tag': 'input', 'type': 'text', 'required': True,
            'id': 'google_optimize_id', 'name': 'google_optimize_id', 'placeholder': 'OPT-XXXXXXX'},
        {'label': 'GAds ID:', 'tag': 'input', 'type': 'text', 'required': True,
            'id': 'gads_id', 'name': 'gads_id', 'placeholder': '纯数字xxxxxx'},
        {'label': 'GAds Label:', 'tag': 'input', 'type': 'text', 'required': True,
            'id': 'gads_label', 'name': 'gads_label', 'placeholder': 'xxxxxx'},
        {'label': 'Hotjar Site ID:', 'tag': 'input', 'type': 'text', 'required': True,
         'id': 'hotjar_site_id', 'name': 'hotjar_site_id', 'placeholder': '308960x'},
        {'label': '训练AI的命令:', 'tag': 'textarea', 'id': 'sys_prompt', 'name': 'sys_prompt', 'required': True,
            'rows': '5', 'placeholder': '你想让AI按什么标准给询盘打分?'},
        {'tag': 'input', 'type': 'submit', 'value': '生成我的Json'}
    ]
    endpoint = request.path.lstrip('/')
    return render_template(endpoint+'.jinja2', js_file='js/'+endpoint+'.js', form_data=form_data)


@gtm_json_blueprint.route('/generate_json', methods=['POST'])
def generate_json():
    ga4_id = request.form['ga4_id']
    google_optimize_id = request.form['google_optimize_id']
    gads_id = request.form['gads_id']
    gads_label = request.form['gads_label']
    hotjar_site_id = request.form['hotjar_site_id']
    sys_prompt = request.form['sys_prompt']

    # Get the directory of the current Python script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Go one level up from the 'routes' directory
    parent_dir = os.path.dirname(current_dir)

    # Build the absolute path for the 'gtm.json' file
    gtm_json_path = os.path.join(parent_dir, 'resources', 'gtm.json')

    with open(gtm_json_path, 'r') as f:
        gtm_json = json.load(f)  # Load JSON as a Python object
        gtm_json = replace_placeholders(
            gtm_json, ga4_id, google_optimize_id, gads_id, gads_label, hotjar_site_id, sys_prompt)

    return jsonify(gtm_json)


def replace_placeholders(json_obj, ga4_id, google_optimize_id, gads_id, gads_label, hotjar_site_id, sys_prompt):
    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            json_obj[key] = replace_placeholders(
                value, ga4_id, google_optimize_id, gads_id, gads_label, hotjar_site_id, sys_prompt)
    elif isinstance(json_obj, list):
        for i, value in enumerate(json_obj):
            json_obj[i] = replace_placeholders(
                value, ga4_id, google_optimize_id, gads_id, gads_label, hotjar_site_id, sys_prompt)
    elif isinstance(json_obj, str):
        return json_obj.replace('ga4_id_replace', ga4_id) \
            .replace('google_optimize_id_replace', google_optimize_id) \
            .replace('gads_id_replace', gads_id) \
            .replace('gads_label_replace', gads_label) \
            .replace('hotjar_site_id_replace', hotjar_site_id) \
            .replace('sys_prompt_replace', sys_prompt)
    return json_obj


def register_routes(app):
    app.register_blueprint(gtm_json_blueprint)
