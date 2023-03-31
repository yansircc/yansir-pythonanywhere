from flask import Blueprint, request, render_template, jsonify
from golem import Golem, openai_api_key
import re


generate_post_blueprint = Blueprint('generate_post', __name__)

@generate_post_blueprint.route('/generate-post', methods=['GET'])
def generate_post():
    return render_template('generate-post.html')

@generate_post_blueprint.route('/generate_post', methods=['POST'])
def generate_html():
    data = request.get_json()
    title = ' '.join(re.findall(r'[a-zA-Z\s]+', data['user_input']))
    post_type = data['post_type']
    smmarized_trained_data = data['smmarized_trained_data']

    sys_prompt = "The following information is about you identity and your business. You will read it in the first person: " + smmarized_trained_data
    
    if post_type == 'response_post':
        max_word_count = 1000
        response_post_golem = Golem(openai_api_key, sys_prompt=sys_prompt, max_tokens=int(max_word_count*1.2))
        user_input = f'''
        From you angle of view, Write a blog post(around {max_word_count} words) about {title}. 
        Keep in mind that you need to:
        1. Insert images for every 300 words using this API:http://source.unsplash.com/800x450/?keywords-here;
        2. Inset a resources link for those keywords which need data support;
        3. Split the paragraph whenever you encounter a period;
        4. The post need to be output in English and html format;
        Here is a example of what you should do:
        ----------------
        <h1>What is a response post?</h1>
        <img src="https://source.unsplash.com/800x450/?keywords-here" alt="featured image">
        <p>Grab attention in the frist paragraph. Multiple rhetorical questions or a fabricated story.(80 words)</p>
        <p>In second paragraph, provide a brief and helpful answer just like Google featured snippet and bold it.(80 words)</p>
        <p>Leave the reader wanting more, maintaining their interest in continuing to read.(30 words)</p>
        <h2>Use related question as heading2, for example: Should I use response posts to rank my website?</h2>
        <p>Related answer here, don't forget to bold keywords and find related images from unsplash.</p>
        <h2>More related questions</h2>
        <p>Relate answers</p>
        <h2>Conclusion</h2>
        <p>Summary this post within 80 words.</p>
        ----------------
        '''

        response = response_post_golem.response(user_input)
        
    elif post_type == 'listicle':
        pass
    elif post_type == 'pillar_post':
        pass
    else:
        return jsonify(error="Invalid post type")

    #html = mistune.markdown(response)
    return jsonify({'response': response})

def register_routes(app):
    app.register_blueprint(generate_post_blueprint)