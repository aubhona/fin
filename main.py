from app import app
from flask import flash, make_response, redirect, render_template, request, session, url_for
from service import *


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")
        is_in, uid, name = log_reg(login, password, 1)
        if is_in:
            session["id"] = uid
            flash(f"Добро пожаловать, {name}!", "success")
            return redirect(url_for("head"))
        else:
            flash("Неправильный пароль или логин.", "danger")
    return render_template("login.html")

@app.route("/head", methods = ["GET", "POST"])
def head():
    if session.get("id"):
        last_oper = ls_op(session["id"])
        max_pr_cat, max_pr, pop_cat = oper(session["id"])
        img = f"{session['id']}-diag2.png"
        response = make_response(render_template("head.html", img = img, last_oper = last_oper, max_pr_cat = max_pr_cat, max_pr = max_pr, pop_cat = pop_cat))
        response.set_cookie("", "", expires=datetime.now()+timedelta(hours=2))
        return response
    else:
        return redirect(url_for("index"))

@app.route("/registration", methods = ["GET", "POST"])
def reg():
    if request.method == "POST":
        login = request.form.get("login")
        name = request.form.get("name")
        surname = request.form.get("surname")
        password = request.form.get("password")
        password_rep = request.form.get("password_rep")
        is_in = log_reg(login, None, 2)
        if is_in[0]:
            flash("Такой логин уже используется. Придумайте другой.", "warning")
        elif password != password_rep:
            flash("Пароли не совпадают.", "warning")
        else:
            uid = log_reg(login, password, 3, name = name, surname = surname)
            session["id"] = uid
            flash(f"Добро пожаловать, {name}!", "success")
            return redirect(url_for("head"))
    return render_template("registration.html")

@app.route("/logout")
def logout():
    if session.get("id"):
        session.pop("id")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug = True)