from app.app import app
from flask import (
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from app.service import *

count_oper = 9


@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404


@app.route("/")
def index():
    if session.get("id"):
        return redirect(url_for("head"))
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("id"):
        return redirect(url_for("head"))
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")
        is_in, uid, name, surname = log_reg(login, password, 1)
        if is_in:
            session["id"] = uid
            session["name"] = name
            session["surname"] = surname
            session["login"] = login
            session["expences"] = check_db_exp(uid)
            session.permanent = True
            flash(f"Добро пожаловать, {name}!", "success")
            return redirect(url_for("head"))
        else:
            flash("Неправильный пароль или логин.", "danger")
    return render_template("login.html")


@app.route("/head", methods=["GET", "POST"])
def head():
    if session.get("id"):
        last_oper = ls_op(session["id"])
        res1 = ""
        res2 = ""
        max_pr_cat, max_pr, pop_cat = oper(session["id"])
        img = ""
        if "date" not in session:
            if session["expences"]:
                img = create_diagram_2(session["id"], None)
                if img:
                    session["date"] = datetime.now().strftime("%Y-%m")
        elif (session["date"] != datetime.now().strftime("%Y-%m")) and (
            session["expences"]
        ):
            img = create_diagram_2(session["id"], None)
            if img:
                session["date"] = datetime.now().strftime("%Y-%m")
        elif session["date"] == datetime.now().strftime("%Y-%m"):
            img = f"{session['id']}-diag2.png"
        if request.method == "POST":
            btn_reg = request.form.get("reg")
            btn_sr = request.form.get("sr")
            cat = request.form.get("cat")
            if cat:
                if btn_sr:
                    res_cur, res_next = calculate_remaining_expenses_using_ema(
                        session["id"], cat
                    )
                    if res_cur:
                        res_cur = round(res_cur, 2)
                        res_next = round(res_next, 2)
                        res1 = f"По категории {cat.lower()} вы, скорее всего, потратите до конца месяца {res_cur} руб."
                        res2 = f"По категории {cat.lower()} вы, скорее всего, потратите в следующем месяце {res_next} руб."
                    else:
                        res1 = ""
                        res2 = ""
                        flash("Недостаточно операций для прогнозирования.", "warning")
                elif btn_reg:
                    if count_month(session["id"], cat):
                        res_cur, res_next = calculate_remaining_expenses_using_linreg(
                            session["id"], cat
                        )
                    else:
                        res_cur, res_next = None, None
                    if res_cur:
                        res_cur = round(res_cur, 2)
                        res_next = round(res_next, 2)
                        res1 = f"По категории {cat.lower()} вы, скорее всего, потратите до конца месяца {res_cur} руб."
                        res2 = f"По категории {cat.lower()} вы, скорее всего, потратите в следующем месяце {res_next} руб."
                    else:
                        res1 = ""
                        res2 = ""
                        flash(
                            "Расчёт по линейной регрессии работает, если по даной категории есть данные от 6 месяцев.",
                            "info",
                        )
            else:
                flash("Выберите категорию прогнозирования.", "warning")
        response = make_response(
            render_template(
                "head.html",
                img=img,
                last_oper=last_oper,
                max_pr_cat=max_pr_cat,
                max_pr=max_pr,
                pop_cat=pop_cat,
                res1=res1,
                res2=res2,
            )
        )
        return response
    else:
        flash("Пожалуйста авторизуйтесь.", "danger")
        return redirect(url_for("login"))


@app.route("/registration", methods=["GET", "POST"])
def reg():
    if session.get("id"):
        return redirect(url_for("head"))
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
            uid = log_reg(login, password, 3, name=name, surname=surname)
            session["id"] = uid
            session["expences"] = 0
            session["name"] = name
            session["surname"] = surname
            session["login"] = login
            session.permanent = True
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
        if session.get("len"):
            session.pop("len")
        if session.get("par"):
            session.pop("par")
        if session.get("base"):
            session.pop("base")
    return redirect(url_for("/"))


@app.route("/add", methods=["GET", "POST"])
def add():
    if session.get("id"):
        if request.method == "POST":
            price = int(request.form.get("price"))
            date = request.form.get("date")
            type_oper = request.form.get("type")
            if type_oper == "+":
                oper_add(session["id"], price, date)
                flash("Успешно добавлено.", "success")
            else:
                cat = request.form.get("cat")
                if cat:
                    res = oper_add(session["id"], price, date, cat=cat)
                    if res is None:
                        flash("Успешно добавлено.", "success")
                    else:
                        flash(
                            "Операция добвлена в историю, но общий остаток баланса не изменен, так как балана недостаточно.",
                            "warning",
                        )
                else:
                    flash("Выберите категорию траты.", "warning")
                session["expences"] += 1
        return render_template("add.html")
    else:
        flash("Пожалуйста авторизуйтесь.", "danger")
        return redirect(url_for("login"))


@app.route("/diagram", methods=["GET", "POST"])
def diagram():
    if session.get("id"):
        img = ""
        if request.method == "POST":
            period = int(request.form.get("time"))
            diag = int(request.form.get("diag"))
            if session["expences"]:
                if diag == 1:
                    img = create_diagram_1(session["id"], period=period)
                else:
                    img = create_diagram_2(session["id"], period=period)
                    if "date" in session:
                        session.pop("date")
            if not img:
                flash("Диграмма не может быть создана, пока нет расходов.", "info")
        return render_template("diagram.html", img=img)
    else:
        flash("Пожалуйста авторизуйтесь.", "danger")
        return redirect(url_for("login"))


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if session.get("id"):
        b_prof = calculate_operations_relatively_base(session["id"], None, None, 1)
        b_exp = calculate_operations_relatively_base(session["id"], None, None, 2)
        b_tot = calculate_operations_relatively_base(session["id"], None, None, 3)
        if session.get("base"):
            b_prof = calculate_operations_relatively_base(
                session["id"], session["base"][1][1:], session["base"][1][0], 1
            )[0]
            b_exp = calculate_operations_relatively_base(
                session["id"], session["base"][1][1:], session["base"][1][0], 2
            )[0]
            if b_tot >= 0:
                b_tot = calculate_operations_relatively_base(
                    session["id"], session["base"][1][1:], session["base"][1][0], 3
                )[0]
            else:
                flash("Общая сумма не пересчитывается, когда она отрицательна.", "info")
            b_prof = round(b_prof, 2)
            b_exp = round(b_exp, 2)
            b_tot = round(b_tot, 2)
            b_prof = str(b_prof) + " усл. ед"
            b_tot = str(b_tot) + " усл. ед"
            b_exp = str(b_exp) + " усл. ед"
        else:
            b_prof = str(b_prof) + " руб."
            b_tot = str(b_tot) + " руб."
            b_exp = str(b_exp) + " руб."
        if request.method == "POST":
            btn_ips = request.form.get("ips")
            btn_pas = request.form.get("pas")
            if btn_pas:
                old_password = request.form.get("old_password")
                if log_reg(session["login"], old_password, 1)[0]:
                    new_password = request.form.get("new_password")
                    reap_new_password = request.form.get("reap_new_password")
                    if new_password == reap_new_password:
                        log_reg(session["login"], new_password, 4)
                        flash("Пароль успешно сменён.", "success")
                    else:
                        flash("Пароли не совпадают.", "warning")
                else:
                    flash("Неправильный пароль.", "danger")
            elif btn_ips:
                try:
                    per = int(request.form.get("per"))
                    b_prof = calculate_operations_relatively_base(
                        session["id"], None, None, 1
                    )
                    b_exp = calculate_operations_relatively_base(
                        session["id"], None, None, 2
                    )
                    b_tot = calculate_operations_relatively_base(
                        session["id"], None, None, 3
                    )
                    b_prof = (
                        str(round(recalculate_balance(session["id"], per, 1), 2))
                        + " руб."
                    )
                    b_exp = (
                        str(round(recalculate_balance(session["id"], per, 2), 2))
                        + " руб."
                    )
                    if b_tot >= 0:
                        b_tot = (
                            str(round(recalculate_balance(session["id"], per, 3), 2))
                            + " руб."
                        )
                    else:
                        flash(
                            "Общая сумма не пересчитывается, когда она отрицательна.",
                            "info",
                        )
                except Exception:
                    flash("Введите срок.", "warning")
        return render_template(
            "profile.html",
            name=session["name"],
            surname=session["surname"],
            sum_prof=b_prof,
            sum_exp=b_exp,
            sum_tot=b_tot,
            base=session.get("base"),
        )
    else:
        flash("Пожалуйста авторизуйтесь.", "danger")
        return redirect(url_for("login"))


@app.route("/history", methods=["GET", "POST"])
def history():
    operat = []
    xlx = ""
    if session.get("len"):
        operat = read_file(session["id"], session["len"])
    if session.get("id"):
        if request.method == "POST":
            btn_his = request.form.get("history")
            btn_xlx = request.form.get("xlx_history")
            btn_del = request.form.get("del_history")
            btn_base = request.form.get("base")
            btn_del_base = request.form.get("del_base")
            if btn_his or btn_xlx:
                check = request.form.get("check")
                if check:
                    sdate = None
                    edate = None
                else:
                    sdate = request.form.get("time1")
                    edate = request.form.get("time2")
                if sdate and edate:
                    try:
                        min_sum = int(request.form.get("min"))
                        max_sum = int(request.form.get("max"))
                    except Exception:
                        min_sum = float("-inf")
                        max_sum = float("inf")
                        flash(
                            "Вы не указали ограничение, поэтому покажутся операции с любой суммой.",
                            "info",
                        )
                    typ1 = request.form.get("prof")
                    typ2 = request.form.get("ex")
                    if typ1 or typ2:
                        if not typ1:
                            typ1 = ""
                        if not typ2:
                            typ2 = ""
                            cat = []
                        else:
                            al = request.form.get("all")
                            if not al:
                                cat = set()
                                for i in range(count_oper):
                                    categ = request.form.get(f"ex{i+1}")
                                    if categ:
                                        cat.add(categ)
                            else:
                                cat = "all"
                        if typ2:
                            if cat:
                                operat = get_oper(
                                    session["id"],
                                    sdate,
                                    edate,
                                    min_sum,
                                    max_sum,
                                    typ1 + typ2,
                                    cat=cat,
                                )
                                session["len"] = save_file(session["id"], operat)
                                session["par"] = [
                                    sdate,
                                    edate,
                                    min_sum,
                                    max_sum,
                                    typ1 + typ2,
                                    list(cat),
                                ]
                                xlx = save_excel(
                                    session["id"],
                                    sdate,
                                    edate,
                                    min_sum,
                                    max_sum,
                                    typ1 + typ2,
                                    cat=cat,
                                )
                            else:
                                flash("Вы не указали категорию трат.", "warning")
                        else:
                            operat = get_oper(
                                session["id"],
                                sdate,
                                edate,
                                min_sum,
                                max_sum,
                                typ1 + typ2,
                                cat=cat,
                            )
                            session["len"] = save_file(session["id"], operat)
                            session["par"] = [
                                sdate,
                                edate,
                                min_sum,
                                max_sum,
                                typ1 + typ2,
                                list(cat),
                            ]
                            xlx = save_excel(
                                session["id"],
                                sdate,
                                edate,
                                min_sum,
                                max_sum,
                                typ1 + typ2,
                                cat=cat,
                            )
                    else:
                        flash("Вы не указали тип операции.", "warning")
                else:
                    if check:
                        try:
                            min_sum = int(request.form.get("min"))
                            max_sum = int(request.form.get("max"))
                        except Exception:
                            min_sum = float("-inf")
                            max_sum = float("inf")
                            flash(
                                "Вы не указали ограничение, поэтому покажутся операции с любой суммой.",
                                "info",
                            )
                        typ1 = request.form.get("prof")
                        typ2 = request.form.get("ex")
                        if typ1 or typ2:
                            if not typ1:
                                typ1 = ""
                            if not typ2:
                                typ2 = ""
                                cat = []
                            else:
                                al = request.form.get("all")
                                if not al:
                                    cat = set()
                                    for i in range(count_oper):
                                        categ = request.form.get(f"ex{i+1}")
                                        if categ:
                                            cat.add(categ)
                                else:
                                    cat = "all"
                            if typ2:
                                if cat:
                                    operat = get_oper(
                                        session["id"],
                                        sdate,
                                        edate,
                                        min_sum,
                                        max_sum,
                                        typ1 + typ2,
                                        cat=cat,
                                    )
                                    session["len"] = save_file(session["id"], operat)
                                    session["par"] = [
                                        sdate,
                                        edate,
                                        min_sum,
                                        max_sum,
                                        typ1 + typ2,
                                        list(cat),
                                    ]
                                    xlx = save_excel(
                                        session["id"],
                                        sdate,
                                        edate,
                                        min_sum,
                                        max_sum,
                                        typ1 + typ2,
                                        cat=cat,
                                    )
                                else:
                                    flash("Вы не указали категорию трат.", "warning")
                            else:
                                operat = get_oper(
                                    session["id"],
                                    sdate,
                                    edate,
                                    min_sum,
                                    max_sum,
                                    typ1 + typ2,
                                    cat=cat,
                                )
                                session["len"] = save_file(session["id"], operat)
                                session["par"] = [
                                    sdate,
                                    edate,
                                    min_sum,
                                    max_sum,
                                    typ1 + typ2,
                                    list(cat),
                                ]
                                xlx = save_excel(
                                    session["id"],
                                    sdate,
                                    edate,
                                    min_sum,
                                    max_sum,
                                    typ1 + typ2,
                                    cat=cat,
                                )
                        else:
                            flash("Вы не указали тип операции.", "warning")
                    else:
                        operat = []
                        flash("Введите начало и конец периода.", "warning")
            elif btn_del:
                if session.get("len"):
                    oper = []
                    for j, i in operat:
                        op = request.form.get(i)
                        if op:
                            del_oper(session["id"], i)
                            if i[0] == "-":
                                session["expences"] -= 1
                            if session.get("base"):
                                if session["base"][1] == i:
                                    session.pop("base")
                        else:
                            oper.append((j, i))
                    operat = oper.copy()
                    session["len"] = save_file(session["id"], operat)
                    xlx = save_excel(
                        session["id"],
                        sdate=session["par"][0],
                        edate=session["par"][1],
                        min_sum=session["par"][2],
                        max_sum=session["par"][3],
                        typ=session["par"][4],
                        cat=set(session["par"][5]),
                    )
            elif btn_base:
                oper = False
                if session.get("base"):
                    session.pop("base")
                operat = get_oper(
                    session["id"],
                    sdate=session["par"][0],
                    edate=session["par"][1],
                    min_sum=session["par"][2],
                    max_sum=session["par"][3],
                    typ=session["par"][4],
                    cat=set(session["par"][5]),
                )
                if session.get("len"):
                    for j, i in operat:
                        op = request.form.get(i)
                        if op and (not session.get("base")):
                            session["base"] = (j, i)
                        else:
                            if op:
                                oper = True
                    if oper:
                        flash(
                            "Вы указали больше 1 базовой операции, поэтому базовой будет считаться первая  выбранная операция.",
                            "info",
                        )
            elif btn_del_base and session.get("base"):
                session.pop("base")
        if session.get("base"):
            expenses, profits = calculate_operations_relatively_base(
                session["id"], session["base"][1][1:], session["base"][1][0], 4
            )
            dic = {}
            for i in range(len(operat)):
                dic[operat[i][1]] = operat[i][0]
            for i in range(len(profits)):
                if ("+" + str(profits[i][0])) in dic:
                    mes = dic["+" + str(profits[i][0])]
                    prob_2 = mes.rfind(" ")
                    prob_1 = mes.rfind(" ", 0, prob_2 - 1)
                    dic["+" + str(profits[i][0])] = (
                        mes[: prob_1 + 1] + str(round(profits[i][1], 2)) + " усл. ед."
                    )
            for i in range(len(expenses)):
                if ("-" + str(expenses[i][0])) in dic:
                    mes = dic["-" + str(expenses[i][0])]
                    prob_2 = mes.rfind(" ")
                    prob_1 = mes.rfind(" ", 0, prob_2 - 1)
                    dic["-" + str(expenses[i][0])] = (
                        mes[: prob_1 + 1] + str(round(expenses[i][1], 2)) + " усл. ед."
                    )
            for i in range(len(operat)):
                operat[i] = (dic[operat[i][1]], operat[i][1])
        if not xlx:
            xlx = "Info.txt"
        return render_template(
            "history.html", oper=operat, xlx=xlx, base=session.get("base")
        )
    else:
        flash("Пожалуйста авторизуйтесь.", "danger")
        return redirect(url_for("login"))
