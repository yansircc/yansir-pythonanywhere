from flask import Blueprint, request, render_template
import json
import os

gtm_json_blueprint = Blueprint('gtm_json', __name__)

@gtm_json_blueprint.route('/gtm-json', methods=['GET'])
def gtm_json():
    return render_template('gtm-json.html')

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