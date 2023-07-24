from flask import Blueprint, request, render_template
from golem import Golem, openai_api_key
from navigator import navigator
from cookies import create_cookie
from queue import Queue
from xmlrpc import client as xmlrpc_client
from wordpress_xmlrpc.methods import media, posts
from wordpress_xmlrpc import Client, WordPressPost
import json
from PIL import Image
import requests
from io import BytesIO
from werkzeug.utils import secure_filename
import os
import re
from midjourney_api import TNL
import time
import markdown
import markdown.extensions.tables
import concurrent.futures
from uuid import uuid4

mj_md_blueprint = Blueprint('mj_md', __name__)
response_queue = Queue()
# NextLeg API
next_leg_token = os.getenv("NEXT_LEG_TOKEN")
tnl = TNL(next_leg_token)

creds = {
    'endpoint': 'https://nosunthx.com/xmlrpc.php',
    'username': os.getenv('NO_SUN_THX_ADMIN'),
    'password': os.getenv('NO_SUN_THX_PASSWORD')
}

@mj_md_blueprint.route('/mj-md')
@navigator
@create_cookie
def mj_md():
    form_data = [
        {'label': '文件上传：', 'tag': 'input', 'type': 'file', 'id': 'file', 'name': 'file',
            'required': 'true'},
        {'tag': 'input', 'type': 'submit', 'id': 'submit', 'value': '提交文档'}
    ]
    endpoint = request.path.lstrip('/')
    return render_template(endpoint+'.jinja2', js_file='js/'+endpoint+'.js', form_data=form_data)

# [已测试]把文本中所有的二级内容和MJ命令解析出来
def parse_file(file_path:str) -> tuple:
    with open(file_path, 'r') as file:
        content = file.read()

    h2_content_regex = r"@ .*?\n\n(.*?)\n\n## "
    mj_commands_regex = r"\n\n@ .*?imagine prompt:(.*?)\n\n"

    h2_contents = re.findall(h2_content_regex, content, re.DOTALL)
    mj_commands = re.findall(mj_commands_regex, content, re.DOTALL)

    return mj_commands, h2_contents

# 传入MJ命令，输出一张MJ的4 in 1图片的字典，其中有图片的ID
def next_leg_post_api(prompt:str, max_retries:int=3) -> dict:
    for i in range(max_retries):
        try:
            response = tnl.imagine(prompt)
            return response
        except requests.exceptions.ConnectionError or requests.exceptions.JSONDecodeError:
            if i < max_retries - 1:  # i is zero indexed
                time.sleep(5)  # wait for 5 seconds before trying again
                continue
            else:
                raise

# 传入图片ID，获取图片进度
def next_leg_get_api(message_id:str) -> dict:
    response = tnl.get_message_and_progress(message_id)
    return response

# [已测试]传入二级内容，使用ChatGPT获取一组图片名、alt和总结
def request_openai_api(h2_content:str) -> tuple:
    user_input = h2_content
    session_id = "mj_md"
    sys_prompt = '''
                You are a function that takes in a string and converts it into three things:
                1. Summarize the string within 50 words.
                2. This text needs to be accompanied by a suitable img with an English name.
                3. Generate a suitable ALT for this img.
                Return a JSON object in the following format:
                {"text_summary": "...", "img_name": "upf_tshirt.png", "alt_description": "UPF fabric t-shirt"}
                IMPORTANT: The format must be exactly as shown above otherwise the system will not work.
             '''
    mj_golem = Golem(openai_api_key, session_id, sys_prompt=sys_prompt, is_stream=False)
    response = next(mj_golem.response(user_input))

    json_str = json.loads(response)
    img_name = json_str.get("img_name")
    alt_description = json_str.get("alt_description")
    text_summary = json_str.get("text_summary")

    return img_name, alt_description, text_summary

# [已测试]传入图片URL，获取图片
def get_nextleg_img(img_url:str) -> bytes:
    url = "https://api.thenextleg.io/getImage"
    payload = json.dumps({
    "imgUrl": img_url
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + next_leg_token
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response

# 下载、优化图片并上传到WP
def optimize_and_upload_img(url:str, file_name:str, alt:str, width:int, format:str, quality:int, creds:dict, max_retries:int=3) -> tuple:
    # Download the image
    response = get_nextleg_img(url)

    # Open the image
    img = Image.open(BytesIO(response.content))

    # If the image has an alpha channel, convert it to RGB
    if img.mode in ('RGBA', 'LA'):
        img = img.convert("RGB")

    # Resize the image
    wpercent = (width / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((width, hsize), Image.Resampling.LANCZOS)

    # Save the image
    file_path = os.path.join(os.path.dirname(__file__), 'tmp')
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    
    file_name = file_name.replace(" ", "_").split('.')[0] + '_' + str(uuid4()) + '.' + format.lower()

    img_path = os.path.join(file_path, file_name)

    img.save(img_path, format, quality=quality)
    print('Saved image to', img_path)

    # Connect to WordPress with the credentials
    for i in range(max_retries):
        try:
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

            return response['url'], file_name, alt
        except requests.exceptions.ConnectionError:
            if i < max_retries - 1:
                time.sleep(3)
                continue
            else:
                raise

# 把图片链接转换成markdown格式
def convert_img_md_link(url:str, title:str, alt:str) -> str:
    shortened_name = '_'.join(title.split('_')[:-1])
    space_separated_name = shortened_name.replace('_', ' ')
    return f'![{alt}]({url} "{space_separated_name}")'

# [已测试]把文本中的MJ内容替换为md链接
def replace_mj_to_md(raw_content:str, replacement_list:list) -> str:
    raw_content = raw_content
    replacement_list = replacement_list
    pattern = r"\n(@ .*?imagine prompt:.*?)\n"
    # 使用re.sub()函数进行替换
    replaced_text = re.sub(pattern, lambda match: replacement_list.pop(0), raw_content)
    return replaced_text

# 用户上传多个文档，发起POST请求
@mj_md_blueprint.route('/fio_imgs', methods=['POST'])
def get_fio_imgs():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    file_path = os.path.join(os.path.dirname(__file__), 'tmp')
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    file_path = os.path.join(file_path, filename)
    file.save(file_path)

    #file = json.loads(raw_content)
    mj_prompts, h2_content = parse_file(file_path)

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

    # Using ThreadPoolExecutor to run the function concurrently
    with concurrent.futures.ThreadPoolExecutor() as executor:
        responses = list(executor.map(request_openai_api, h2_content))

    for response in responses:
        print(response)
        fio_img_names.append(response[0])
        fio_img_alt.append(response[1])
        fio_img_summaries.append(response[2])

    combined_dict = {
        'filename': filename,
        'file_path': file_path,
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
    # 用户提交的data中包含所选的图片序号、文件名和ALT
    data = request.get_json()
    filename = data["filename"]
    file_path = data["file_path"]
    imgs = data["imgs"]
    
    img_md_strings = ['Processing...' for _ in imgs]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(optimize_and_upload_img, img["upscale_img_url"], img["upscale_img_name"], img["upscale_img_alt"], 800, 'jpeg', 90, creds): i for i, img in enumerate(imgs)}
        
        for future in concurrent.futures.as_completed(futures):
            i = futures[future]  # get the original index
            try:
                wp_img_url, img_name, img_alt = future.result()
                img_md_string = convert_img_md_link(wp_img_url, img_name, img_alt)
                img_md_strings[i] = img_md_string
            except Exception as exc:
                print('A task generated an exception: %s' % exc)
                img_md_strings[i] = 'Error processing image: %s' % exc

    with open(file_path, 'r') as file:
        raw_content = file.read()
    replaced_md_string = replace_mj_to_md(raw_content, img_md_strings)

    # 保存替换后的文本
    with open(file_path, 'w') as file:
        file.write(replaced_md_string)

    json_str = json.dumps({
        'filename': filename,
        'file_path': file_path,
        'content': replaced_md_string
    })
    return json_str

# 将文档上传到WP
@mj_md_blueprint.route('/upload_to_wp', methods=['POST'])
def upload_to_wp():
    data = request.get_json()
    file_path = data["file_path"]
    filename = data["filename"].replace("_", " ")
    
    max_retries = 3

    for i in range(max_retries):
        try:
            wp = Client(creds['endpoint'], creds['username'], creds['password'])
            with open(file_path, 'r') as file:
                content = file.read()

            # remove the first line of the content
            content = content.split('\n', 1)[1]
            html = markdown.markdown(content, extensions=['tables'])
            
            post = WordPressPost()
            if filename.endswith('.txt'):
                post.title = filename[:-4]
            elif file.filename.endswith('.md'):
                post.title = filename[:-3]
            else:
                post.title = filename
            post.content = html
            post.post_status = 'draft'
            post.id = wp.call(posts.NewPost(post))
            
            # clean up all files in the tmp folder
            file_path = os.path.join(os.path.dirname(__file__), 'tmp')
            for file in os.listdir(file_path):
                os.remove(os.path.join(file_path, file))

            return 'success', 200
        except requests.exceptions.ConnectionError:
            if i < max_retries - 1:
                time.sleep(3)
                continue
            else:
                raise


def register_routes(app):
    app.register_blueprint(mj_md_blueprint)