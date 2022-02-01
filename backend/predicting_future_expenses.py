import numpy as np
from sklearn.linear_model import LinearRegression

from fin.backend.query import get_data


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
