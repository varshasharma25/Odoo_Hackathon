import os
print("ENV CHECK → DB_NAME:", os.getenv("DB_NAME"))
from flask import Flask
from config import Config
from models import db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

from routes import auth_routes
app.register_blueprint(auth_routes)

if __name__ == "__main__":
    app.run(debug=True)
