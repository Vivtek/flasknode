from flask import Flask
app = Flask(__name__,
            static_folder = "static")

from flasknode import views
from flasknode import static_files
