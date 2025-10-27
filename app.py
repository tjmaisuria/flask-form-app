from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os

app = Flask(__name__)

# --------------------------------------------
# Database connection (Render provides DATABASE_URL)
# --------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

# --------------------------------------------
# Routes
# --------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    email = request.form.get("email")
    address = request.form.get("address")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (first_name, last_name, email, address) VALUES (%s, %s, %s, %s)",
        (firstname, lastname, email, address),
    )
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("thankyou"))

@app.route("/thankyou")
def thankyou():
    return "<h2>Thank you! Your info has been saved successfully.</h2>"

@app.route("/view")
def view():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT first_name, last_name, email, address FROM users;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"users": rows}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
