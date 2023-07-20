from flask import Flask, Blueprint, request, render_template, stream_with_context, send_file, Response
from golem import Golem, openai_api_key
from navigator import navigator
from cookies import create_cookie
from queue import Queue
from xmlrpc import client as xmlrpc_client
from wordpress_xmlrpc.methods import media
from wordpress_xmlrpc import Client, WordPressPost
import json
from PIL import Image
import requests
from io import BytesIO
from werkzeug.utils import secure_filename
import os
import re
import threading
from midjourney_api import TNL
import time

mj_md_blueprint = Blueprint('mj_md', __name__)
response_queue = Queue()
# NextLeg API
token = os.getenv("NEXT_LEG_TOKEN")
tnl = TNL(token)

@mj_md_blueprint.route('/mj-md')
@navigator
@create_cookie
def mj_md():
    form_data = [
        {'label': '文件上传：', 'tag': 'input', 'type': 'file', 'id': 'file', 'name': 'file',
            'placeholder': '输入一段想转为Anki卡片的文本', 'required': 'true'},
        {'tag': 'input', 'type': 'submit', 'id': 'submit', 'value': '提交文档'}
    ]
    endpoint = request.path.lstrip('/')
    return render_template(endpoint+'.jinja2', js_file='js/'+endpoint+'.js', form_data=form_data)

# [已测试]把文本中所有的二级内容和MJ命令解析出来
def parse_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    h2_content_regex = r"@ .*?\n\n(.*?)\n\n## "
    mj_commands_regex = r"\n\n@ .*?imagine prompt:(.*?)\n\n"

    h2_contents = re.findall(h2_content_regex, content, re.DOTALL)
    mj_commands = re.findall(mj_commands_regex, content, re.DOTALL)

    return mj_commands, h2_contents

# 传入MJ命令，输出一张MJ的4 in 1图片的字典，其中有图片的ID
def next_leg_post_api(prompt):
    response = tnl.imagine(prompt)
    return response

# 传入图片ID，获取图片进度
def next_leg_get_api(message_id):
    response = tnl.get_message_and_progress(message_id)
    return response

# [已测试]传入二级内容，使用ChatGPT获取一组图片名、alt和总结
def request_openai_api(h2_content):
    user_input = h2_content
    session_id = "mj_md"
    sys_prompt = '''
                You are a function that takes in a string and converts it into three things:
                1. Summarize the string within 50 words.
                2. This text needs to be accompanied by a suitable img with an English name.
                3. Generate a suitable ALT for this img.
                Return a JSON object in the following format:
                {"text_summary": "...", "img_name": "upf_tshirt.png", "alt_description": "UPF fabric t-shirt"}
             '''
    mj_golem = Golem(openai_api_key, session_id, sys_prompt=sys_prompt, is_stream=False)
    response = next(mj_golem.response(user_input))

    json_str = json.loads(response)
    img_name = json_str.get("img_name")
    alt_description = json_str.get("alt_description")
    text_summary = json_str.get("text_summary")

    return img_name, alt_description, text_summary

# [已测试]优化图片
def optimize_img(url:str, file_name:str, width:int, format:str, quality:int):
    # Download the image
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Open the image
    img = Image.open(BytesIO(response.content))

    # Resize the image
    wpercent = (width / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((width, hsize), Image.ANTIALIAS)

    # Save the image
    file_path = os.path.join(os.path.dirname(__file__), 'tmp')
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    img_path = os.path.join(file_path, file_name + '.' + format.lower())

    img.save(img_path, format, quality=quality)
    print('Saved image to', img_path)
    return img_path

# [已测试]把图片上传到WP
def upload_img_to_wp(img_path:str, creds:dict):
    # Connect to WordPress with the credentials
    wp = Client(creds['endpoint'], creds['username'], creds['password'])

    # Prepare metadata for the img
    data = {
        'name': os.path.basename(img_path),
        'type': 'image/jpeg'
    }

    # Read the downloaded img and upload it to WordPress
    with open(img_path, 'rb') as img:
        data['bits'] = xmlrpc_client.Binary(img.read())
    response = wp.call(media.UploadFile(data))

    # Clean up the temporary file
    os.remove(img_path)

    return response['url']

# 把图片链接转换成markdown格式
def convert_img_md_link(url:str, title:str, alt:str):
    return f'![{alt}]({url} "{title}")'

# [已测试]把文本中的MJ内容替换为md链接
def replace_mj_to_md(raw_content, replacement_list):
    raw_content = raw_content
    replacement_list = replacement_list
    pattern = r"\n(@ .*?imagine prompt:.*?)\n"
    # 使用re.sub()函数进行替换
    replaced_text = re.sub(pattern, lambda match: replacement_list.pop(0), raw_content)
    return replaced_text

# 用户上传多个文档，发起POST请求
@mj_md_blueprint.route('/fio_imgs', methods=['POST'])
def get_fio_imgs():
    file = request.files['file']

    filename = secure_filename(file.filename)
    file_path = os.path.join(os.path.dirname(__file__), 'tmp')
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    file_path = os.path.join(file_path, filename)
    file.save(file_path)

    #file = json.loads(raw_content)
    mj_prompts, h2_content = parse_file(file_path)
    
    print(type(mj_prompts), type(h2_content))
    print(len(mj_prompts), len(h2_content))

    fio_img_ids = []
    fio_img_names = []
    fio_img_alt = []
    fio_img_summaries = []

    for prompt in mj_prompts:
        print(prompt)
        fio_img = next_leg_post_api(prompt)
        if fio_img['success']:
            fio_img_ids.append(fio_img['messageId'])
            print(fio_img['messageId'])
            time.sleep(1)

    for content in h2_content:
        response = request_openai_api(content)
        fio_img_names.append(response[0])
        fio_img_alt.append(response[1])
        fio_img_summaries.append(response[2])

    with open(file_path, 'r') as file:
        raw_content = file.read()

    combined_dict = {
        'raw_content': raw_content,
        'imgs': [fio_img_ids, fio_img_names, fio_img_alt, fio_img_summaries]
    }

    json_str = json.dumps(combined_dict)
    return json_str

# NextLeg达到100%后，返回图片信息并加入队列
@mj_md_blueprint.route('/webhook', methods=['POST'])
def webhook():
    post_data = request.data
    img_data = json.loads(post_data)
    img_id = img_data['originatingMessageId']
    img_urls = img_data['imageUrls']
    optimize_img(img_data['imageUrl'], img_id, 800, 'jpeg', 90)
    for index, img in enumerate(img_urls):
        optimize_img(img, img_id + '_' + str(index+1) , 800, 'jpeg', 90)
    return 'success'


# 用户返回所选图片，返回替换为md格式的原文
@mj_md_blueprint.route('/mj_to_md', methods=['POST'])
def get_upscale_imgs_number():
    # # 用户提交的data中包含所选的图片序号、文件名和ALT
    data = request.get_json()
    raw_content = data["raw_text"]
    imgs = data["imgs"]
    mj_get_url = "http://localhost:5000/upscale"
    creds = {
        'endpoint': 'https://nosunthx.com/xmlrpc.php',
        'username': os.getenv('NO_SUN_THX_ADMIN'),
        'password': os.getenv('NO_SUN_THX_PASSWORD')
    }
    
    img_md_strings = []
    for img in imgs:
        title = img["upscale_img_name"]
        alt = img["upscale_img_alt"]
        number = img["upscale_img_number"]
        response = requests.get(mj_get_url, json={
            "file_name": title,
            "number": number
        })
        upscale_img_url = response.json().get("upscale_img_url")
        optimized_img = optimize_img(upscale_img_url, img["upscale_img_number"], 800, 'jpeg', 90)
        wp_img_url = upload_img_to_wp(optimized_img, creds)
        img_md_string = convert_img_md_link(wp_img_url, title, alt)
        img_md_strings.append(img_md_string)

    replaced_md_string = replace_mj_to_md(raw_content, img_md_strings)
    return replaced_md_string


def register_routes(app):
    app.register_blueprint(mj_md_blueprint)