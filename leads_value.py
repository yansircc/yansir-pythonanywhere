from flask import Blueprint, request
from ga4mp import GtagMP
from uuid import uuid4
from flask_cors import CORS
import openai
import re
import random
import time

leads_value_blueprint = Blueprint('leads-value', __name__)
CORS(leads_value_blueprint, origins=["https://forkmover.com"])

@leads_value_blueprint.route('/leads-value', methods=['POST'])
def leads_value():
    data = request.get_json()
    leads_content = data['leads_content']
    sys_prompt = data['sys_prompt']
    max_tokens = data['max_tokens']
    temperature = data['temperature']
    measurement_id = data['measurement_id']
    api_secret = data['api_secret']
    ads_conversion_id = data['ads_conversion_id']
    ads_aw_id = re.match(r'(.+?)/', ads_conversion_id).group(1)
    client_id = data['client_id'] if data['client_id'] is not None else ("%0.10d" % random.randint(0,9999999999) + "." + str(int(time.time())))

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{'role':'system', 'content':sys_prompt},{'role':'user', 'content':leads_content}],
        max_tokens=max_tokens,
        temperature=temperature
    )
    chatgpt_response = response.choices[0].message['content']

    raw_num = re.search(r'\d+', re.sub('B2B', '', chatgpt_response)).group()
    leads_score = round(pow(float(raw_num), 1.5)/10, 2)
    send_custom_event(measurement_id, ads_aw_id, api_secret, ads_conversion_id, client_id, leads_score)
    return_string = '这条询盘（Uid：' + str(client_id) + '）综合评分为：' + str(leads_score) + '(和AI评分略不同)，评分已成功传递给GA，以下是来自AI的评价：\n----------\n' + chatgpt_response + '\n\n==========\n\n'
    return return_string

# custom functions below
def send_custom_event(measurement_id, ads_aw_id, api_secret, ads_conversion_id, client_id, leads_value):
    ga = GtagMP(measurement_id=measurement_id, api_secret=api_secret, client_id=client_id)
    gads = GtagMP(measurement_id=ads_aw_id, api_secret=api_secret, client_id=client_id)

    leads_value_event_type = 'conversion'
    leads_value_event_parameters = {
        'send_to': ads_conversion_id,
        'value': leads_value,
        'currency': 'USD',
        'transaction_id': str(uuid4())
    }
    event = {'name': leads_value_event_type, 'params': leads_value_event_parameters }
    events = [event]

    ga.send( events )
    gads.send( events )

def register_routes(app):
    app.register_blueprint(leads_value_blueprint)