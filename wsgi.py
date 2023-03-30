from flask_app import app
from dotenv import load_dotenv
import os

if os.environ.get("FLASK_ENV") == "development":
    project_folder = os.path.expanduser('~')
else:
    project_folder = os.path.expanduser('~/mysite')

load_dotenv(os.path.join(project_folder, '.env'))

if __name__ == "__main__":
    app.run(debug=True)