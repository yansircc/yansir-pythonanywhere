from flask import Blueprint, request, send_file, render_template_string, render_template, Response, jsonify, url_for
import openai
import re
import markdown
from weasyprint import HTML
import io
import base64
import uuid
from markupsafe import Markup
from post_ideas import sys_prompt

generate_post_blueprint = Blueprint('generate_post', __name__)

@generate_post_blueprint.route('/personas', methods=['GET'])
def personas():
    return render_template('personas.html')

@generate_post_blueprint.route('/convert-to-md', methods=['POST'])
def convert_to_md():
    data = request.get_json()
    title = ' '.join(re.findall(r'[a-zA-Z\s]+', data['title']))
    post_type = data['postType']
    trained_data = data['dataTrained']
    
    if post_type == 'response-post':
        client_request = f'''
        From you angle of view, Write a blog post(around 1000 words) about {title}, and note that the post need to be output in English and markdown format.
        1. The first paragraph(80 words) of the article should grab attention, which can be done using multiple rhetorical questions or a fabricated story. 
        2. In the second paragraph(max 80 words), provide a brief and helpful answer to the main question of the article which will strive for Google featured snippet. Wrap the entire paragraph with two asterisks(for example: **wrapped strings**).
        3. The third paragraph(30 words) should leave the reader wanting more, maintaining their interest in continuing to read. 
        4. Come up with additional questions highly relevant to the topic, use them as H2. Each H2 must attract the attention of the user in the form of a question.
        5. Wrap all keywords that need data support resources or keywords that deserve further reading with two asterisks.
        6. Split the paragraph whenever you encounter a period/full stop.
        '''
    elif post_type == 'listicle':
        pass
    elif post_type == 'pillar-post':
        pass
    else:
        return jsonify(error="Invalid post type")

    markdown_string = chatgpt(trained_data, client_request)
    return jsonify(markdown_string=markdown_string)

@generate_post_blueprint.route('/download-pdf', methods=['POST'])
def download_response_post():
    data = request.get_json()
    markdown_string = data['markdown_string']
    title = '_'.join(re.findall(r'[a-zA-Z\s]+', data['title']))
    pdf_data = md_to_pdf(markdown_string)
    pdf_b64 = base64.b64encode(pdf_data).decode('utf-8')

    file_id = str(uuid.uuid4())
    download_url = url_for('generate_post.serve_pdf', file_id=file_id)
    if not hasattr(generate_post_blueprint, 'pdf_store'):
        generate_post_blueprint.pdf_store = {}
    generate_post_blueprint.pdf_store[file_id] = {'pdf_data': pdf_b64, 'title': title}

    return jsonify(download_url=download_url)

@generate_post_blueprint.route('/serve-pdf/<file_id>', methods=['GET'])
def serve_pdf(file_id):
    stored_data = generate_post_blueprint.pdf_store.get(file_id)
    if stored_data is None:
        abort(404)
    pdf_b64 = stored_data['pdf_data']
    title = stored_data['title'].strip()
    pdf_data = base64.b64decode(pdf_b64)
    return Response(pdf_data, content_type='application/pdf', headers={'Content-Disposition': f'attachment;filename={title}.pdf'})

def chatgpt(trained_data, client_request):
    sys_prompt = "The following information is about you identity and your business. You will read it in the first person: " + re.sub(r"Based on the above information.*", "", trained_data)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{'role':"system", "content":sys_prompt}] + [{'role': "user", "content":client_request}]
    )
    chatgpt_response = response.choices[0].message['content']
    return chatgpt_response

def md_to_pdf(markdown_string):
    html = markdown.markdown(markdown_string)
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <style>
            body {font-family: Arial, sans-serif;}
            h1 {
                font-size: 2.5rem;
                font-weight: bold;
                margin-top: 2rem;
                margin-bottom: 1rem;
            }
            
            h2 {
                font-size: 2rem;
                font-weight: bold;
                margin-top: 2rem;
                margin-bottom: 1rem;
            }
            
            h3 {
                font-size: 1.75rem;
                font-weight: bold;
                margin-top: 2rem;
                margin-bottom: 1rem;
            }
            
            h4 {
                font-size: 1.5rem;
                font-weight: bold;
                margin-top: 2rem;
                margin-bottom: 1rem;
            }
            
            h5 {
                font-size: 1.25rem;
                font-weight: bold;
                margin-top: 2rem;
                margin-bottom: 1rem;
            }
            
            h6 {
                font-size: 1rem;
                font-weight: bold;
                margin-top: 2rem;
                margin-bottom: 1rem;
            }
            
            b, strong {
                font-weight: bold;
            }
            
            ul {
                list-style-type: disc;
                margin-top: 1rem;
                margin-bottom: 1rem;
                margin-left: 2rem;
            }
            
            ol {
                list-style-type: decimal;
                margin-top: 1rem;
                margin-bottom: 1rem;
                margin-left: 2rem;
            }
            
            li {
                margin-top: 0.5rem;
                margin-bottom: 0.5rem;
            }
        </style>
    </head>
    <body>
    {{ content }}
    </body>
    </html>
    '''
    rendered_html = render_template_string(html_template, content=Markup(html))
    pdf_io = io.BytesIO()
    HTML(string=rendered_html).write_pdf(pdf_io)
    pdf_data = pdf_io.getvalue()
    return pdf_data

def register_routes(app):
    app.register_blueprint(generate_post_blueprint)