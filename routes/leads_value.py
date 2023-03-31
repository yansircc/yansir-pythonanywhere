from flask import Blueprint, request, jsonify
from flask_cors import CORS
from golem import Golem, openai_api_key

leads_value_blueprint = Blueprint('leads-value', __name__)

CORS(leads_value_blueprint, origins=["*"])

@leads_value_blueprint.route('/leads-value', methods=['POST'])
def leads_value():
    data = request.get_json()
    sys_prompt = data['sys_prompt']
    sys_prompt_prefix = "You're a rating machine. You will rate the inquiries on a scale of 0-100. "
    sys_prompt_suffix = " You always output score first head and then explain the reasons."
    leads_check_golem = Golem(openai_api_key, sys_prompt=sys_prompt, sys_prompt_prefix=sys_prompt_prefix, sys_prompt_suffix=sys_prompt_suffix, max_tokens=150, temperature=0.2)

    user_input = data['leads_content']
    response = leads_check_golem(user_input)

    return jsonify({'response': response})
    # raw_num = re.search(r'\d+', re.sub('B2B', '', response)).group()
    # leads_score = round(pow(float(raw_num), 1.5)/10, 2)
    # return_string = '这条询盘（Uid：' + str(client_id) + '）综合评分为：' + str(leads_score) + '(和AI评分略不同)，评分已成功传递给GA，以下是来自AI的评价：\n----------\n' + chatgpt_response + '\n\n==========\n\n'
    # return return_string


def register_routes(app):
    app.register_blueprint(leads_value_blueprint)