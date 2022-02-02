import matplotlib.pyplot as plt
from time import time

from query import get_stat


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

    path = "../resources/{0}.png".format(str(uid) + "#1")
    plt.savefig(path, facecolor="#FFE4E1")
    # plt.show()


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
    path = "../resources/{0}.png".format(str(uid) + "#2")
    plt.savefig(path, facecolor="#FFE4E1")
    # plt.show()


create_diagram_2(uid=4, period=12)
