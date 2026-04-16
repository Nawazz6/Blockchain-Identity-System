from flask import Flask, render_template
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.bank_routes import bank_bp
from config import SECRET_KEY, UPLOAD_FOLDER, ENCRYPTED_FOLDER
import os

app = Flask(__name__)
app.secret_key = SECRET_KEY

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["ENCRYPTED_FOLDER"] = ENCRYPTED_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(bank_bp)

@app.route("/")
def landing():
    return render_template("landing.html")

import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))