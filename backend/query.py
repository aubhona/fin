from backend.models import *
from datetime import datetime, timedelta
from collections import defaultdict

def get_stat(uid, per): #date format: YYYY-mm-dd
    dic = defaultdict(int)
    date = datetime.date(datetime.today() - timedelta(weeks=4 * per))
    for expense in Expenses.query.filter_by(user_id=uid).all():
        if datetime.date() >= date:
            dic[expense.cat] += expense.price
    return list(dic.items())  # [(cat1, price1), (cat2, price2)]


def get_data(uid, cat):  # date format: YYYY-mm-dd
    dic = defaultdict(int)
    months = set()
    for expense in Expenses.query.filter_by(user_id=uid).all():
        months.add(expense.date[:7])
    for expense in Expenses.query.filter_by(user_id=uid).all():
        if expense.cat == cat:
            dic[expense.date[:7]] += expense.price
    return list(dic.items())  # [(date1, price1), (date2, price2)] date format: YYYY-mm


def get_data_for_xlx(uid, sdate, edate):  # date format: YYYY-mm-dd
    sdate, edate = datetime.date(datetime.strptime(sdate, "%Y-%m-%d")), datetime.date(
        datetime.strptime(edate, "%Y-%m-%d"))
    dicex = []
    dicprof = []
    diccat = []
    dicexpr = []
    dicprofpr = []
    for expense in Expenses.query.filter_by(user_id=uid).all():
        if sdate <= datetime.date(datetime.strptime(expense.date, "%Y-%m-%d")) <= edate:
            date = f"{expense.date[8:]}.{expense.date[5:7]}.{expense.date[:4]}"
            dicex.append(date)
            diccat.append(expense.cat)
            dicexpr.append(expense.price)
    for profit in Profits.query.filter_by(user_id=uid).all():
        if sdate <= datetime.date(datetime.strptime(profit.date, "%Y-%m-%d")) <= edate:
            date = f"{profit.date[8:]}.{profit.date[5:7]}.{profit.date[:4]}"
            dicprof.append(date)
            dicprofpr.append(expense.price)
    return dicex, diccat, dicexpr, dicexpr, dicprof, dicprofpr


def get_base_data(uid):
    expenses = []
    profits = []
    balance = [int(Users.query.filter_by(id=uid).one().balance)]
    for expense in Expenses.query.filter_by(user_id=uid).all():
        expenses.append((int(expense.id), int(expense.price)))
    for profit in Profits.query.filter_by(user_id=uid).all():
        profits.append((int(profit.id), int(profit.price)))
    # -------------------------------
    base_operation_id = [(666, "+/-")]
    # -------------------------------

    return balance + expenses + profits + base_operation_id

def is_in_db(login, password, code):
    try:
        user = Users.query.filter_by(login = login).one()
        if code == 1:
            return user.password == md5(password.encode('utf8')).hexdigest(), user.id, user.name
        else:
            return True, None, None
    except Exception as e:
        return False, None, None

def regis(login, password, name, surname):
    user = Users(name, surname, login, password)
    db.session.add(user)
    db.session.commit()
    return user.id

def las(uid):
    date = None
    cat = None
    pr = None
    try:
        for expense in Expenses.query.filter_by(user_id=uid).all():
            date_cur = datetime.date(datetime.strptime(expense.date, "%Y-%m-%d"))
            if date is None:
                date = date_cur
                cat = expense.cat
                pr = expense.price
            else:
                if date_cur>=date:
                    date = date_cur
                    cat = expense.cat
                    pr = expense.price
        if date is None:
            raise "There is not operation"
        return cat, pr
    except Exception as e:
        return "There is not operation", None

def all_op(uid):
    date_month = datetime.date(datetime.today() - timedelta(weeks=4))
    date_month = date_month.strftime("%m")
    dic = {}
    cat = None
    price = None
    try:
        for expense in Expenses.query.filter_by(user_id=uid).all():
            date_cur = datetime.date(datetime.strptime(expense.date, "%Y-%m-%d"))
            if date_cur.strftime("%m") == date_month:
                if expense.cat in dic:
                    dic[expense.cat][0] += expense.price
                    dic[expense.cat][1] +=1
                else:
                    dic[expense.cat] = [expense.price, 1]
                if cat is None:
                    cat = expense.cat
                    price = expense.price
                else:
                    if price<expense.price:
                        cat = expense.cat
                        price = expense.price
        if cat is None:
            raise "There is not operation"
        max_cat = float("-inf")
        max_cat_pr = float("-inf")
        pop_cat = float("-inf")
        pop_cat_count = float("-inf")
        for i in dic:
            if dic[i][0]>max_cat_pr:
                max_cat_pr = dic[i][0]
                max_cat = i
            if dic[i][1]>pop_cat_count:
                pop_cat_count = dic[i][1]
                pop_cat = i
        return price, cat, pop_cat, pop_cat_count, max_cat, max_cat_pr
    except Exception as e:
        return "There is not operation", None, None, None, None, None


