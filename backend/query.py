from models import *
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd


def get_stat(uid, per): #date format: YYYY-mm-dd
    dic = defaultdict(int)
    date = datetime.date(datetime.today() - timedelta(weeks=4 * per))
    for expense in Expenses.query.filter_by(user_id=uid).all():
        if datetime.date() >= date:
            dic[expense.cat] += expense.price
    return list(dic.items()) #[(cat1, price1), (cat2, price2)]

def get_data(uid, cat): #date format: YYYY-mm-dd 
    dic = defaultdict(int)
    months = set()
    for expense in Expenses.query.filter_by(user_id=uid).all():
        months.add(expense.date[:7])
    for expense in Expenses.query.filter_by(user_id=uid).all():
        if expense.cat == cat:
            dic[expense.date[:7]]+=expense.price
    return list(dic.items()) #[(date1, price1), (date2, price2)] date format: YYYY-mm

def get_data_for_xlx(uid, sdate, edate): #date format: YYYY-mm-dd
    sdate, edate = datetime.date(datetime.strptime(sdate, "%Y-%m-%d")), datetime.date(datetime.strptime(edate, "%Y-%m-%d"))
    dicex = []
    dicprof = []
    diccat = []
    dicexpr = []
    dicprofpr = []
    for expense in Expenses.query.filter_by(user_id=uid).all():
        if sdate<=datetime.date(datetime.strptime(expense.date, "%Y-%m-%d"))<=edate:
            date = f"{expense.date[8:]}.{expense.date[5:7]}.{expense.date[:4]}"
            dicex.append(date)
            diccat.append(expense.cat)
            dicexpr.append(expense.price)
    for profit in Profits.query.filter_by(user_id=uid).all():
        if sdate<=datetime.date(datetime.strptime(profit.date, "%Y-%m-%d"))<=edate:
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
