from flask import Flask, redirect
import os
import openai

from builder import register_routes as register_builder_routes
from paid_chat import register_routes as register_paid_chat_routes
from business import register_routes as register_business_routes
from leads_value import register_routes as register_leads_value_routes

app = Flask(__name__)
# Register routes from builder.py
register_builder_routes(app)
# Register routes from paid_chat.py
register_paid_chat_routes(app)
# Register routes from business.py
register_business_routes(app)
# Register routes from leads_value.py
register_leads_value_routes(app)

# Set OpenAI API key
openai.api_key = os.environ.get('API_KEY')

@app.route('/')
def index():
    return redirect('/builder')

# @app.route('/personas')
# def personas():
#     return render_template('personas.html')

if __name__ == '__main__':
    app.run()