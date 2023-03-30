from flask import Blueprint, request, jsonify
from flask_cors import CORS
# import re
from golem import Golem
import os

leads_value_blueprint = Blueprint('leads-value', __name__)

CORS(leads_value_blueprint, origins=["*"])

@leads_value_blueprint.route('/leads-value', methods=['POST'])
def leads_value():
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    data = request.get_json()
    sys_prompt = data['sys_prompt']
    leads_check_golem = Golem(openai_api_key, sys_prompt, max_tokens=100, temperature=0.2)

    user_input = data['leads_content']
    response = leads_check_golem(user_input)

    return jsonify({'response': response})
    # raw_num = re.search(r'\d+', re.sub('B2B', '', response)).group()
    # leads_score = round(pow(float(raw_num), 1.5)/10, 2)
    # return_string = '这条询盘（Uid：' + str(client_id) + '）综合评分为：' + str(leads_score) + '(和AI评分略不同)，评分已成功传递给GA，以下是来自AI的评价：\n----------\n' + chatgpt_response + '\n\n==========\n\n'
    # return return_string


def register_routes(app):
    app.register_blueprint(leads_value_blueprint)