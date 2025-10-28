from flask import Flask, render_template, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
import os
import pandas as pd
from io import BytesIO

app = Flask(__name__)

# ---------------------
# DATABASE CONFIG
# ---------------------
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------------
# DATABASE MODEL
# ---------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=False)

# Ensure tables exist
with app.app_context():
    db.create_all()

# ---------------------
# ROUTES
# ---------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    address = request.form.get('address')

    if not (first_name and last_name and email and address):
        return "All fields are required!", 400

    user = User(first_name=first_name, last_name=last_name, email=email, address=address)
    db.session.add(user)
    db.session.commit()

    return redirect('/view')


@app.route('/view')
def view():
    users = User.query.all()
    return render_template('view.html', users=users)


@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    keyword = ''
    if request.method == 'POST':
        keyword = request.form.get('keyword', '').strip()
        if keyword:
            results = User.query.filter(
                (User.first_name.ilike(f"%{keyword}%")) |
                (User.last_name.ilike(f"%{keyword}%")) |
                (User.email.ilike(f"%{keyword}%")) |
                (User.address.ilike(f"%{keyword}%"))
            ).all()
    return render_template('search_results.html', users=results, keyword=keyword)


@app.route('/export')
def export():
    users = User.query.all()
    data = [{
        "First Name": u.first_name,
        "Last Name": u.last_name,
        "Email": u.email,
        "Address": u.address
    } for u in users]

    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    return send_file(output, download_name="user_data.xlsx", as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
