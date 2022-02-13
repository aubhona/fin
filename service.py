import matplotlib
import matplotlib.pyplot as plt
from time import time
from backend.query import *
import numpy as np
from sklearn.linear_model import LinearRegression
import pandas as pd
import requests
import json

matplotlib.use('Agg')

def calculate_remaining_expenses_using_ema(uid, categories):
    data = get_data(uid, categories)
    data_dict = {}
    for i in data:
        if i[0] in data:
            data_dict[i[0]] += int(i[1])
        else:
            data_dict[i[0]] = int(i[1])
    data = list(data_dict.items())
    n = len(data)
    k = 2 / (n + 1)
    data.sort(key=lambda x: (int(x[0].split("-")[0]), int(x[0].split("-")[1])))
    data_copy = data.copy()
    current_month = int(data[-1][1])
    del data[-1]
    for i in range(len(data)):
        if i == 0:
            data[i] = int(data[i][1])
        else:
            data[i] = k * int(data[i][1]) + data[i - 1] * (1 - k)
    for_current = data[-1] - current_month

    if for_current < 0:
        for_current = 0
    data_copy[-1] = (data_copy[-1][0], data_copy[-1][1] + for_current)
    data_copy.append(("1", 0))
    for i in range(len(data_copy)):
        if i == 0:
            data_copy[i] = int(data_copy[i][1])
        else:
            data_copy[i] = k * int(data_copy[i][1]) + data_copy[i - 1] * (1 - k)
    for_next = data_copy[-1]

    return for_current, for_next


def calculate_remaining_expenses_using_linreg(uid, categories):
    months = []
    data = get_data(uid, categories)
    data_dict = {}
    for i in data:
        if i[0] in data:
            data_dict[i[0]] += int(i[1])
        else:
            data_dict[i[0]] = int(i[1])
    data = list(data_dict.items())
    model1 = LinearRegression(normalize=True)
    x = []
    y = []
    data.sort(key=lambda i: (int(i[0].split("-")[0]), int(i[0].split("-")[1])))
    current_month = int(data[-1][1])
    data_copy = data.copy()
    data_second_method = data.copy()
    data_second_method_copy = data.copy()
    del data[-1]
    for month in range(len(data) - 4):
        months = list(map(lambda i: int(i[1]), data[month:month + 3]))
        x.append(sum(months))
        y.append(int(data[month + 3][1]))
    xx = np.array(x).reshape((-1, 1))
    yy = np.array(y)
    model1.fit(xx, yy)
    data_for_pred = sum(list(map(lambda i: int(i[1]), data))[-3:])
    pred = model1.predict(np.array(data_for_pred).reshape((-1, 1)))
    for_current1 = pred[0] - current_month
    if for_current1 < 0:
        for_current1 = 0
    data_copy[-1] = (data_copy[-1][0], data_copy[-1][1] + for_current1)
    months.append(list(map(lambda i: int(i[1]), data_copy[-4:-1])))
    x.append(sum(months[-1]))
    y.append(int(data_copy[-1][1]))
    xx = np.array(x).reshape((-1, 1))
    yy = np.array(y)
    model2 = LinearRegression(normalize=True)
    model2.fit(xx, yy)
    data_for_pred = sum(list(map(lambda i: int(i[1]), data_copy))[-3:])
    pred = model1.predict(np.array(data_for_pred).reshape((-1, 1)))
    for_next1 = pred[0]
    # return for_current1, for_next1

    x = []
    y = []
    del data_second_method[-1]
    for month in range(len(data_second_method) - 1):
        x.append(int(data_second_method[month][1]))
        y.append(int(data_second_method[month + 1][1]))
    xx = np.array(x).reshape((-1, 1))
    yy = np.array(y)
    model2.fit(xx, yy)
    pred = model2.predict(np.array([int(data_second_method[-1][1])]).reshape((-1, 1)))
    for_current2 = pred[0] - current_month
    if for_current2 < 0:
        for_current2 = 0
    data_second_method_copy[-1] = (data_second_method_copy[-1][0], data_second_method_copy[-1][1] + for_current2)
    x.append(int(data_second_method_copy[-2][1]))
    y.append(int(data_second_method_copy[-1][1]))
    xx = np.array(x).reshape((-1, 1))
    yy = np.array(y)
    model2.fit(xx, yy)
    pred = model2.predict(np.array([int(data_second_method_copy[-1][1])]).reshape((-1, 1)))
    for_next2 = pred[0]
    return (for_current1 + for_current2) / 2, (for_next2 + for_next1) / 2

def create_diagram_1(uid=1, period=1):
    data = get_stat(uid, period)
    values = []
    labels = []
    width = 0.55
    for item in data:
        labels.append(item[0])
        values.append(int(item[1]))

    fig, ax = plt.subplots()

    ax.bar(labels, values, width, label='Total', color="#696969")

    ax.set_ylabel('Потрачено в общем')
    ax.set_title('Расходы по категориям')
    ax.set_facecolor("#C0C0C0")

    path = "static/img/{0}.png".format(str(uid) + "-diag1")
    plt.savefig(path, facecolor="#FFE4E1")
    # plt.show()
    return "{0}.png".format(str(uid) + "-diag1")


def create_diagram_2(uid=1, period=1):
    data = get_stat(uid, period)
    sizes = []
    labels = []
    for item in data:
        labels.append(item[0])
        sizes.append(int(item[1]))
    summ = sum(sizes)
    explode = [0] * len(sizes)
    for i in range(len(sizes)):
        sizes[i] = (sizes[i] / summ) * 100
    sorted_sizes = sorted(sizes)

    for i in sorted_sizes:
        index = sizes.index(i)
        explode[index] = 0.8 * (i / 100) ** 2
    explode[sizes.index(min(sizes))] = 0

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=80)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax1.set_title('Расходы по категориям')
    path = "static/img/{0}.png".format(str(uid) + "-diag2")
    plt.savefig(path, facecolor="#FFE4E1")
    # plt.show()
    return "{0}.png".format(str(uid) + "-diag2")

def save_excel(uid, sdate, edate):
    dicex, diccat, dicexpr, dicexpr, dicprof, dicprofpr = get_data_for_xlx(uid, sdate, edate)
    list1 = pd.DataFrame({"Дата":dicex, "Категория": diccat, "Расход(в руб.)":dicexpr})
    list2 = pd.DataFrame({"Дата":dicprof, "Доход(в руб.)": dicprofpr})
    tab = {"Доходы":list2, "Расходы":list1}
    writer = pd.ExcelWriter(f"static/resources/{uid}-export_to_excel.xlsx", engine='xlsxwriter')
    tab["Доходы"].to_excel(writer, sheet_name="Доходы", index=False)
    tab["Расходы"].to_excel(writer, sheet_name="Расходы",index=False)
    writer.save()
    return f"{uid}-export_to_excel.xlsx"

def calculate_operations_relatively_base(user_id):
    data = list(get_base_data(user_id))
    base_operation_id = [int(data[-1][0]), int(data[-1][1])]
    del data[-1]
    profits = data[2]
    expenses = data[1]
    if base_operation_id[1] == "+":
        base_operation = list(filter(lambda x: int(x[0]) == int(base_operation_id[0]), profits))[1]
    else:
        base_operation = list(filter(lambda x: int(x[0]) == int(base_operation_id[0]), expenses))[1]
    recalculated_profits = list(map(lambda x: (x[0], float(x[1]) / base_operation), profits))
    recalculated_expenses = list(map(lambda x: (x[0], float(x[1]) / base_operation), expenses))
    recalculated_balance = [int(data[0]) / base_operation]
    return recalculated_balance + recalculated_expenses + recalculated_profits

def log_reg(login, password, code, name = None, surname = None):
    if code == 1:
        return is_in_db(login, password, 1)
    elif code == 2:
        return is_in_db(login, "", 2)
    elif code == 3:
        return regis(login, password, name = name, surname = surname, code = 1)
    else:
        regis(login, password, code = 2)

def ls_op(uid):
    cat, pr = las(uid)
    if cat == "There is not operation":
        return "Вы не совершали расходы."
    return f"{cat.lower()} - {pr} рублей."

def oper(uid):
    price, cat, pop_cat, pop_cat_count, max_cat, max_cat_pr = all_op(uid)
    if price=="There is not operation":
        return "Вы не совершали расходы.", "Вы не совершали расходы.", "Вы не совершали расходы."
    max_pr = f" {price} рублей на категорию: {cat.lower()}."
    pop_cat = f"категорию {pop_cat.lower()}, Вы совершали расходы по этой категории {pop_cat_count} раз."
    max_cat = f"категорию {max_cat.lower()}, в сумме Вы потратили {max_cat_pr} рублей на эту категорию."
    return max_cat, max_pr, pop_cat

def oper_add(uid, price, date, cat = None):
    if cat is None:
        db_add_prof(uid, price, date)
    else:
        db_add_exp(uid, price, date, cat)

def get_expences(uid, per):
    return get_db_expences(uid, per)

def recalculate_balance(uid, period) -> float:
    # PV = get_balance(uid=uid)
    PV = 100

    url = "https://apidata.mos.ru/v1/datasets/62025/rows?api_key=d6dd03633051cdca213e0a016186697f&$orderby=global_id"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    text = response.text
    data = json.loads(text)[-1]
    IPC = float(data["Cells"]["Value"])

    FV = PV * (1. - (period / 12.) * ((IPC - 100.) / 100.))
    if FV < 0:
        FV = 0.

    return FV
