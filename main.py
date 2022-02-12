from crypt import methods
from app import app
from flask import flash, make_response, redirect, render_template, request, session, url_for
from backend.service import *
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")
        is_in, uid, name = log(login, password)
        if is_in:
            session["id"] = uid
            flash(f"Добро пожаловать, {name}!", "success")
            return redirect(url_for("head"))
        else:
            flash("Неправильный пароль или логин.", "warning")
            print("Asfasfasgasgagagasgasgasgasgsdagmmsdgmsdgmmsgdmsadgmsadgmmdgs")
    return render_template("login.html")

@app.route("/head", methods = ["GET", "POST"])
def head():
    if "id" in session:
        response = make_response(render_template("head.html"))
        response.set_cookie(expires=datetime.now()+timedelta(hours=2))
        return response
    else:
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug = True)