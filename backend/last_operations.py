import matplotlib.pyplot as plt
from time import time

from query import get_stat


def create_diagram(uid=1, period=1):
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

    path = "../resources/{0}.png".format(str(uid) + "." + str(int(time())))
    plt.savefig(path, facecolor="#FFE4E1")
    # plt.show()

create_diagram()
