from numpy import diag
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
        is_in, uid, name, surname = log_reg(login, password, 1)
        if is_in:
            session["id"] = uid
            session["name"] = name
            session["surname"] = surname
            session["login"] = login
            flash(f"Добро пожаловать, {name}!", "success")
            return redirect(url_for("head"))
        else:
            flash("Неправильный пароль или логин.", "danger")
    return render_template("login.html")

@app.route("/head", methods = ["GET", "POST"])
def head():
    if session.get("id"):
        last_oper = ls_op(session["id"])
        if last_oper == "Вы не совершали расходы.":
            session["expences"] = False
        else:
            session["expences"] = True
        max_pr_cat, max_pr, pop_cat = oper(session["id"])
        img = f"{session['id']}-diag2.png"
        if ("date" not in session) and (session["expences"] == True):
            session["date"] = datetime.now().strftime("%Y-%m")
            img = create_diagram_2(session["id"], None)
        elif (session["date"] != datetime.now().strftime("%Y-%m")) and (session["expences"] == True):
            session["date"] = datetime.now().strftime("%Y-%m")
            img = create_diagram_2(session["id"], None)
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
            session["expences"] = False
            session["name"] = name
            session["surname"] = surname
            session["login"] = login
            flash(f"Добро пожаловать, {name}!", "success")
            return redirect(url_for("head"))
    return render_template("registration.html")

@app.route("/logout")
def logout():
    if session.get("id"):
        session.pop("id")
        session.pop("name")
        session.pop("surname")
        session.pop("login")
        if session.get("date"):
            session.pop("date")
        if session.get("expences"):
            session.pop("expences")
    return redirect("/")

@app.route("/add", methods = ["GET", "POST"])
def add():
    if request.method == "POST":
        price = int(request.form.get("price"))
        date = request.form.get("date")
        type_oper = request.form.get("type")
        if type_oper == "+":
            oper_add(session["id"], price, date)
        else:
            cat = request.form.get("cat")
            if cat:
                oper_add(session["id"], price, date, cat = cat)
                flash("Успешно добавлено.", "success")
            else:
                flash("Выберите категорию траты", "warning")
            session["expences"] = True
    return render_template("add.html")

@app.route("/diagram", methods = ["GET", "POST"])
def diagram():
    img = ""
    if request.method == "POST":
        period = int(request.form.get("time"))
        diag = int(request.form.get("diag"))
        if session["expences"]:
            if diag==1:
                img = create_diagram_1(session["id"], period=period)
            else:
                img = create_diagram_2(session["id"], period=period)
                if "date" in session:
                    session.pop("date")
    return render_template("diagram.html", img = img)

@app.route("/profile", methods = ["GET", "POST"])
def profile():
    if request.method == "POST":
        old_password = request.form.get("old_password")
        if log_reg(session["login"], old_password, 1)[0]:
            new_password = request.form.get("new_password")
            reap_new_password = request.form.get("reap_new_password")
            if new_password == reap_new_password:
                log_reg(session["login"], new_password, 4)
                flash("Пароль успешно сменён", "success")
            else:
                flash("Пароли не совпадают", "warning")
        else:
            flash("Неправильный пароль", "danger")
    return render_template("profile.html", name = session["name"], surname = session["surname"])

@app.route("/history", methods = ["GET", "POST"])
def history():
    operat = get_expences(session["id"], 12)
    xlx = save_excel(session["id"], "2020-01-01", "2022-03-03")
    return render_template("history.html", oper = operat, xlx = xlx)
if __name__ == "__main__":
    app.run(debug = True)