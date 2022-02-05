from flask import g
from models import *
from datetime import datetime, timedelta
from collections import defaultdict


def get_stat(uid, per):
    dic = defaultdict(int)
    date = datetime.date(datetime.today() - timedelta(weeks=4 * per))
    for expense in Expenses.query.filter_by(user_id=uid).all():
        if datetime.date(datetime.strptime(expense.date, "%Y-%m-%d")) >= date:
            dic[expense.cat] += expense.price
    return list(dic.items())


def get_data(uid, cat):
    dic = defaultdict(int)
    months = set()
    for expense in Expenses.query.filter_by(user_id=uid).all():
        months.add(expense.date[:7])
    for expense in Expenses.query.filter_by(user_id=uid).all():
        if expense.cat == cat:
            dic[expense.date[:7]] += expense.price
    return list(dic.items())
