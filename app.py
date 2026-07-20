from flask import Flask,render_template
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from config import Config
from models import db, Student

# Blueprints
from routes.auth import auth
from routes.complaint import complaint
from routes.admin import admin
from routes.room import room

app = Flask(__name__)

app.config.from_object(Config)

# Database
db.init_app(app)

# Bcrypt
bcrypt = Bcrypt(app)

import routes.auth
routes.auth.bcrypt = bcrypt

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    return Student.query.get(int(user_id))


with app.app_context():
    db.create_all()

# Register Blueprints
app.register_blueprint(auth)
app.register_blueprint(complaint)
app.register_blueprint(admin)
app.register_blueprint(room)


@app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)
