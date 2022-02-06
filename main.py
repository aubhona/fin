from itsdangerous import json
from backend.models import app
from flask import jsonify, render_template, request

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/first_page.html", methods = ["GET", "POST"])
def firsr_page():
    b = ""
    if request.method == "POST":
        login = request.form.get("login")
        b = 1
    return render_template("first_page.html", bl = b)

@app.route("/history.html")
def f():
    print(235)
    return render_template("history.html")

if __name__ == "__main__":
    app.run(debug = True)