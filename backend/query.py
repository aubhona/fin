from flask import g
from models import *
from datetime import datetime, timedelta
from collections import defaultdict


def get_stat(uid, per) -> list[str, int]:
    dic = defaultdict(int)
    date = datetime.date(datetime.today() - timedelta(weeks=4 * per))
    for expense in Expenses.query.filter_by(user_id=uid).all():
        if datetime.date(datetime.strptime(expense.date, "%Y-%m-%d")) >= date:
            dic[expense.cat] += expense.price
    return list(dic.items())


def get_data(uid, cat) -> list[str, int]:
    dic = defaultdict(int)
    months = set()
    for expense in Expenses.query.filter_by(user_id=uid).all():
        months.add(expense.date[:7])
    for expense in Expenses.query.filter_by(user_id=uid).all():
        if expense.cat == cat:
            dic[expense.date[:7]] += expense.price
    return list(dic.items())


def get_base_data(uid) -> list[float, int]:
    expenses = []
    profits = []
    balance = [get_balance(uid=uid)]
    for expense in Expenses.query.filter_by(user_id=uid).all():
        expenses.append((int(expense.id), int(expense.price)))
    for profit in Profits.query.filter_by(user_id=uid).all():
        profits.append((int(profit.id), int(profit.price)))
    # -------------------------------
    base_operation_id = [(666, "+/-")]
    # -------------------------------

    return balance + expenses + profits + base_operation_id


def get_balance(uid) -> float:
    balance = float(Users.query.filter_by(id=uid).one().balance)
    return balance
