from flask import Flask, redirect
import os
import openai

from routes.builder import register_routes as register_builder_routes
from routes.paid_chat import register_routes as register_paid_chat_routes
from routes.business import register_routes as register_business_routes
from routes.leads_value import register_routes as register_leads_value_routes
from routes.post_ideas import register_routes as register_post_ideas_routes
from routes.generate_post import register_routes as register_generate_post_routes
from routes.gtm_json import register_routes as register_gtm_json_routes

app = Flask(__name__)
register_builder_routes(app)
register_paid_chat_routes(app)
register_business_routes(app)
register_leads_value_routes(app)
register_post_ideas_routes(app)
register_generate_post_routes(app)
register_gtm_json_routes(app)

# Set Flask session secret key
app.secret_key = 'your-secret-key-here'

@app.route('/')
def index():
    return redirect('/builder')

if __name__ == '__main__':
    app.run(debug=True)