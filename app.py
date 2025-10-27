from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define your table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))

# ✅ Create tables at startup (Flask 3.0+ compatible)
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    email = request.form.get("email")
    address = request.form.get("address")

    new_user = User(
        firstname=firstname,
        lastname=lastname,
        email=email,
        address=address
    )
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("thankyou"))

@app.route("/thankyou")
def thankyou():
    return "<h2>Thank you! Your info has been saved successfully.</h2>"

@app.route("/view")
def view():
    users = User.query.all()
    return {"users": [
        {"firstname": u.firstname, "lastname": u.lastname, "email": u.email, "address": u.address}
        for u in users
    ]}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
