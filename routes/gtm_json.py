from flask import Blueprint, request, render_template
import json

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

    with open('resources/gtm.json', 'r') as f:
        gtm_json = f.read()
        gtm_json = gtm_json.replace('ga4_id_replace', ga4_id)
        gtm_json = gtm_json.replace('ga4_api_key_replace', ga4_api_key)
        gtm_json = gtm_json.replace('gads_id_replace', gads_id)
        gtm_json = gtm_json.replace('gads_label_replace', gads_label)
        gtm_json = gtm_json.replace('openai_api_key_replace', openai_api_key)

    return json.dumps(gtm_json)


def register_routes(app):
    app.register_blueprint(gtm_json_blueprint)