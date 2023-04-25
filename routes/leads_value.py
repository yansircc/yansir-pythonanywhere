from flask import Blueprint, request, jsonify, render_template
from flask_cors import CORS
from golem import Golem, openai_api_key
from uuid import uuid4
from navigator import navigator
from cookies import create_cookie
import re

leads_value_blueprint = Blueprint('leads-value', __name__)

CORS(leads_value_blueprint, origins=["*"])



# 测试用
@leads_value_blueprint.route('/gtm-demo', methods=['GET'])
@navigator
@create_cookie
def gtm_json():
    form_data = [
        {'label': '询盘内容:', 'tag': 'textarea', 'id': 'leads_content',
            'rows': '5', 'placeholder': 'some inquiry content'},
        {'tag': 'input', 'type': 'submit', 'value': 'Send to AI'}
    ]
    endpoint = request.path.lstrip('/')
    return render_template(endpoint+'.jinja2', js_file='js/'+endpoint+'.js', form_data=form_data)


@leads_value_blueprint.route('/leads-value', methods=['POST'])
def leads_value():
    data = request.get_json()
    first_party_cookie = data['first_party_cookie']
    leads_content = data['leads_content']
    sys_prompt = data['sys_prompt']
    sys_prompt_prefix = "You're a rating machine. You will rate the inquiries on a scale of 0-100. "
    sys_prompt_suffix = " You always output score first head and then explain the reasons(within 20 words)."
    leads_check_golem = Golem(openai_api_key, first_party_cookie, sys_prompt=sys_prompt,
                              sys_prompt_prefix=sys_prompt_prefix, sys_prompt_suffix=sys_prompt_suffix, temperature=0.2, is_stream=False)

    golem_response = leads_check_golem.response(leads_content)
    for res in golem_response:
        response_str = res
    leads_value = re.findall(r'\d+', response_str)[0]
    leads_value = int(leads_value) if leads_value else 0
    enhance_leads_value = int(round(leads_value ** 1.5 / 3, 0))
    transaction_id = 'uuid_' + str(uuid4()) + '-user_id_'+first_party_cookie
    reson = '\n'.join(response_str.split('\n')[1:])
    response = jsonify({'leads_value': enhance_leads_value,
                       'transaction_id': transaction_id,
                       'reson': reson})
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


def register_routes(app):
    app.register_blueprint(leads_value_blueprint)
