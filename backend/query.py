from backend.models import *
from datetime import datetime, timedelta
from collections import defaultdict

def get_stat(uid, per): #date format: YYYY-mm-dd
    if per is None:
        date = datetime.now().strftime("%Y-%m")+"-01"
        date = datetime.date(datetime.strptime(date, "%Y-%m-%d"))
    else:
        date = datetime.date(datetime.today() - timedelta(weeks=per))
    dic = defaultdict(int)
    for expense in Expenses.query.filter_by(user_id=uid).all():
        if datetime.date(datetime.strptime(expense.date, "%Y-%m-%d")) >= date:
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


def get_data_for_xlx(uid, sdate, edate, min_sum, max_sum):  # date format: YYYY-mm-dd
    dicex = []
    dicprof = []
    diccat = []
    dicexpr = []
    dicprofpr = []
    expenses = []
    profits = []
    if sdate:
        sdate, edate = datetime.date(datetime.strptime(sdate, "%Y-%m-%d")), datetime.date(datetime.strptime(edate, "%Y-%m-%d"))
        for expense in Expenses.query.filter_by(user_id=uid).all():
            if (sdate <= datetime.date(datetime.strptime(expense.date, "%Y-%m-%d")) <= edate) and (min_sum<=expense.price<=max_sum):
                expenses.append(expense)
    else:
        for expense in Expenses.query.filter_by(user_id=uid).all():
            if (min_sum<=expense.price<=max_sum):
                expenses.append(expense)
    expenses.sort(key=lambda x: datetime.date(datetime.strptime(x.date, "%Y-%m-%d")), reverse=True)
    for expense in expenses:
            date = f"{expense.date[8:]}.{expense.date[5:7]}.{expense.date[:4]}"
            dicex.append(date)
            diccat.append(expense.cat)
            dicexpr.append(expense.price)
    if sdate:
        for profit in Profits.query.filter_by(user_id=uid).all():
            if (sdate <= datetime.date(datetime.strptime(profit.date, "%Y-%m-%d")) <= edate) and (min_sum<=profit.price<=max_sum):
                profits.append(profit)
    else:
        for profit in Profits.query.filter_by(user_id=uid).all():
            if (min_sum<=profit.price<=max_sum):
                profits.append(profit)
    profits.sort(key=lambda x: datetime.date(datetime.strptime(x.date, "%Y-%m-%d")), reverse=True)
    for profit in profits:
            date = f"{profit.date[8:]}.{profit.date[5:7]}.{profit.date[:4]}"
            dicprof.append(date)
            dicprofpr.append(profit.price)
    return dicex, diccat, dicexpr, dicexpr, dicprof, dicprofpr


def get_base_data(uid, op_id, typ, code):
    expenses = []
    profits = []
    balance = []
    balance = [get_balance(uid, code)]
    base_operation_id = [(op_id, typ)]
    if code == 4:
        for expense in Expenses.query.filter_by(user_id=uid).all():
            expenses.append((int(expense.id), int(expense.price)))
        for profit in Profits.query.filter_by(user_id=uid).all():
            profits.append((int(profit.id), int(profit.price)))

        base_operation_id = [(op_id, typ)]
    else:
        expense = Expenses.query.filter_by(id=int(op_id)).one()
        expenses.append((int(op_id), expense.price))

    return balance + [expenses] + [profits] + base_operation_id

def is_in_db(login, password, code):
    try:
        user = Users.query.filter_by(login = login).one()
        if code == 1:
            return user.password == md5(password.encode('utf8')).hexdigest(), user.id, user.name, user.surname
        else:
            return True, None, None
    except Exception as e:
        return False, None, None, None

def regis(login, password, name = None, surname = None, code = 0):
    if code == 1:
        user = Users(name, surname, login, password)
        db.session.add(user)
        db.session.commit()
        return user.id
    else:
        user = Users.query.filter_by(login = login).one()
        user.password = md5(password.encode('utf8')).hexdigest()
        db.session.add(user)
        db.session.commit()

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

def db_add_exp(uid, price, date, cat):
    cat = Expenses(uid, price, date, cat)
    user = Users.query.filter_by(id = uid).one()
    user.balance_exp += price
    user.balance_tot -= price
    db.session.add(cat)
    db.session.add(user)
    db.session.commit()

def db_add_prof(uid, price, date):
    prof = Profits(uid, price, date)
    user = Users.query.filter_by(id = uid).one()
    user.balance_tot += price
    user.balance_prof += price
    db.session.add(prof)
    db.session.add(user)
    db.session.commit()

def get_db_expences(uid, sdate, edate, min_sum, max_sum):
    oper = []
    if sdate:
        sdate = datetime.date(datetime.strptime(sdate, "%Y-%m-%d"))
        edate = datetime.date(datetime.strptime(edate, "%Y-%m-%d"))
        for expense in Expenses.query.filter_by(user_id=uid).all():
            if (sdate <= datetime.date(datetime.strptime(expense.date, "%Y-%m-%d")) <= edate) and (min_sum<=expense.price<=max_sum):
                oper.append((datetime.date(datetime.strptime(expense.date, "%Y-%m-%d")), expense.cat, expense.price, expense.id))
    else:
        for expense in Expenses.query.filter_by(user_id=uid).all():
            if  (min_sum<=expense.price<=max_sum):
                oper.append((datetime.date(datetime.strptime(expense.date, "%Y-%m-%d")), expense.cat, expense.price, expense.id))
    return oper

def get_db_profits(uid, sdate, edate, min_sum, max_sum):
    oper = []
    if sdate:
        sdate = datetime.date(datetime.strptime(sdate, "%Y-%m-%d"))
        edate = datetime.date(datetime.strptime(edate, "%Y-%m-%d"))
        for profit in Profits.query.filter_by(user_id=uid).all():
            if (sdate <= datetime.date(datetime.strptime(profit.date, "%Y-%m-%d")) <= edate) and (min_sum<=profit.price<=max_sum):
                oper.append((datetime.date(datetime.strptime(profit.date, "%Y-%m-%d")), profit.price, profit.id))
    else:
        for profit in Profits.query.filter_by(user_id=uid).all():
            if (min_sum<=profit.price<=max_sum):
                oper.append((datetime.date(datetime.strptime(profit.date, "%Y-%m-%d")), profit.price, profit.id))
    return oper

def get_balance(uid, code):
    if code == 1:
        return Users.query.filter_by(id=uid).one().balance_prof
    if code == 2:
        return Users.query.filter_by(id=uid).one().balance_exp
    if code == 3:
        return Users.query.filter_by(id=uid).one().balance_tot

def del_expense(uid, op_id):
    user = Users.query.filter_by(id = uid).one()
    expense = Expenses.query.filter_by(id = op_id).one()
    user.balance_exp -= expense.price
    user.balance_tot += expense.price
    db.session.add(user)
    db.session.delete(expense)
    db.session.commit()

def del_profit(uid, op_id):
    user = Users.query.filter_by(id = uid).one()
    profit = Profits.query.filter_by(id = op_id).one()
    user.balance_tot -= profit.price
    user.balance_prof -= profit.price
    db.session.add(user)
    db.session.delete(profit)
    db.session.commit()

def check_exp(uid):
    count = 0
    try:
        for expense in Expenses.query.filter_by(user_id = uid).all():
            count+=1
    except Exception:
        count = 0
    return count

def count_exp(uid, cat):
    count = 0
    s = set()
    for expense in Expenses.query.filter_by(user_id = uid).all():
        if expense.cat == cat:
            s.add(datetime.date(datetime.strptime(expense.date, "%Y-%m-%d")).strftime("%m"))
    return len(s)
