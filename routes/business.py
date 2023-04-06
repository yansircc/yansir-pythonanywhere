from flask import Blueprint, request, render_template, Response, stream_with_context
from golem import Golem, openai_api_key
from transcripts_db import TranscriptsDB
from navigator import navigator
from queue import Queue
import json

business_blueprint = Blueprint('business', __name__)
response_queue = Queue()
business_db = TranscriptsDB()


@business_blueprint.route('/business')
@navigator
def business():
    form_data = [
        {'label':'关于你的生意：','tag': 'input', 'type': 'text', 'class': 'user_input', 'name': 'my-business-brand-name', 'placeholder': '你的品牌名叫什么？'},
        {'tag': 'input', 'type': 'text', 'class': 'user_input', 'name': 'my-business-location', 'placeholder': '你在哪个国家？'},
        {'tag': 'input', 'type': 'text', 'class': 'user_input', 'name': 'my-business-product-type', 'placeholder': '你做什么产品？'},
        {'tag': 'input', 'type': 'text', 'class': 'user_input', 'name': 'my-business-type', 'placeholder': '你做的是B2B还是B2C？'},
        {'tag': 'input', 'type': 'text', 'class': 'user_input', 'name': 'my-company-type', 'placeholder': '你是工厂还是贸易商？'},
        {'tag': 'input', 'type': 'number', 'class': 'user_input', 'name': 'my-business-company-size', 'placeholder': '你的公司多少人？'},
        {'tag': 'input', 'type': 'text', 'class': 'user_input', 'name': 'my-business-export-country', 'placeholder': '你出口过哪些国家？'},
        {'tag': 'input', 'type': 'text', 'class': 'user_input', 'name': 'my-business-target-audience', 'placeholder': '你的客户可以是什么身份？'},
        {'tag': 'input', 'type': 'text', 'class': 'user_input', 'name': 'my-business-competitive-advantage', 'placeholder': '你和其他对手比有什么优势？'},
        {'tag': 'input', 'type': 'text', 'class': 'user_input', 'name': 'my-business-promotion-channel', 'placeholder': '你目前在用哪些渠道推广？'},
        {'label':'关于你的用户画像：', 'tag': 'input', 'type': 'text', 'class': 'user_input', 'name': 'typical-Client-name', 'placeholder': '他叫什么？'},
        {'tag': 'input', 'type': 'text', 'class': 'user_input', 'name': 'typical-client-location', 'placeholder': '他在哪个国家？'},
        {'tag': 'input', 'type': 'number', 'class': 'user_input', 'name': 'typical-Client-age', 'placeholder': '他年龄多大？'},
        {'tag': 'input', 'type': 'text', 'class': 'user_input', 'name': 'typical-Client-personality', 'placeholder': '他是什么性格？'},
        {'tag': 'input', 'type': 'text', 'class': 'user_input', 'name': 'typical-Client-prefer-product', 'placeholder': '他采购什么产品？'},
        {'tag': 'input', 'type': 'text', 'class': 'user_input', 'name': 'typical-Client-prefer-price-or-quality', 'placeholder': '他对价格和质量哪个更敏感？'},
        {'tag': 'input', 'type': 'text', 'class': 'user_input', 'name': 'typical-Client-position', 'placeholder': '他是什么职位？'},
        {'tag': 'input', 'type': 'text', 'class': 'user_input', 'name': 'typical-Client-prefer-country', 'placeholder': '他偏好在哪些国家采购？'},
        {'tag': 'input', 'type': 'number', 'class': 'user_input', 'name': 'typical-Client-company-size', 'placeholder': '他的公司有多少人？'},
        {'tag': 'input', 'type': 'text', 'class': 'user_input', 'name': 'typical-Client-business-model', 'placeholder': '他的生意怎么赚钱？'},
        {'tag': 'input', 'type': 'text', 'class': 'user_input', 'name': 'typical-Client-prefer-supplier-channel', 'placeholder': '他会通过哪些渠道找供应商？'},
        {'tag': 'input', 'type': 'text', 'class': 'user_input', 'name': 'typical-Client-supplier-priority', 'placeholder': '找供应商时看重什么？'},
        {'tag': 'input', 'type': 'text', 'class': 'user_input', 'name': 'typical-Client-pain-points', 'placeholder': '采购时遇到什么问题会烦心甚至恼怒？'},
        {'tag': 'input', 'type': 'text', 'class': 'user_input', 'name': 'typical-Client-additional-info', 'placeholder': '对于他的描述，有什么要补充的？'},
        {'tag': 'input', 'type': 'submit', 'value': '预训练'}
    ]
    endpoint = request.path.lstrip('/')
    return render_template(endpoint+'.jinja2', js_file='js/'+endpoint+'.js', form_data=form_data)


@business_blueprint.route('/business_golem', methods=['GET', 'POST'])
def business_golem():
    if request.method == 'POST':
        form_data = request.form.to_dict()
        form_data_str = json.dumps(form_data)
        session_id = request.cookies.get('user_id')
        sys_prompt = "You are a successful Chinese business owner. Now, you have to describe your business to ChatGPT."
        user_input_prefix = "This is your business information: "
        user_input_suffix = "A key with the keyword 'PERSONAS' indicates that the value is information about your target audience, and a key with the keyword 'MY-BUSINESS' indicates that the value is information about your business. Now start your description in English within 200 words."
        business_golem = Golem(openai_api_key, session_id, sys_prompt=sys_prompt,
                            user_input_prefix=user_input_prefix, user_input_suffix=user_input_suffix)

        def store_data_in_db(full_reply_content):
            with business_db as db:
                db.create_table('conversation', 'business_prompts')
                db.store_data('conversation', session_id,
                            'business_prompts', full_reply_content)

        response = business_golem.response(form_data_str, store_data_in_db)
        response_queue.put(response)
        return '', 204
    else:
        response = response_queue.get()
        return Response(stream_with_context(response), mimetype='text/event-stream')

def register_routes(app):
    app.register_blueprint(business_blueprint)
