from flask import Blueprint, request, render_template, jsonify
import openai
import re

sys_prompt = "You're a man of few words."

post_ideas_blueprint = Blueprint('post-ideas', __name__)

@post_ideas_blueprint.route('/ideas')
def ideas():
    return render_template('post-ideas.html')

@post_ideas_blueprint.route('/post-ideas', methods=['POST'])
def post_ideas_endpoint():
    data = request.get_json()
    if 'user_trianed_data' in data:
        global sys_prompt
        user_trianed_data = data['user_trianed_data']
        sys_prompt = user_trianed_data
        return jsonify({'success': True})
    else:
        client_request = data['client_request']
        return chatgpt(client_request)
    
def chatgpt(client_request):
    global sys_prompt
    modify_sys_prompt = "The following information is about you identity and your business. You will read it in the first person: " + re.sub(r"Based on the above information.*", "", sys_prompt)
    modify_client_request = "From your angle of view, " + client_request + " Note that the post title should be a clickbait question. Output in this format: [English blog title: Chinese translation], and don't explain anything."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{'role':"system", "content":modify_sys_prompt}] + [{'role': "user", "content":modify_client_request}]
    )
    chatgpt_response = response.choices[0].message['content']
    return chatgpt_response

def register_routes(app):
    app.register_blueprint(post_ideas_blueprint)