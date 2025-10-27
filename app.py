from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import pandas as pd
from flask import send_file
import io

# -----------------------
# App and Database Setup
# -----------------------
app = Flask(__name__)

# Get database URL from Render environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -----------------------
# Database Model
# -----------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))

# Create tables at startup (Flask 3.x compatible)
with app.app_context():
    db.create_all()

# -----------------------
# Routes
# -----------------------
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
    return render_template("view.html", users=users)

# -----------------------

@app.route("/export")
def export():
    # Get all users from database
    users = User.query.all()

    # Convert to list of dicts
    data = [{
        "First Name": u.firstname,
        "Last Name": u.lastname,
        "Email": u.email,
        "Address": u.address
    } for u in users]

    # Create DataFrame
    df = pd.DataFrame(data)

    # Write to Excel in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Users")
    output.seek(0)

    # Send file to user
    return send_file(output, download_name="users.xlsx", as_attachment=True)
# Run the App
# -----------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

