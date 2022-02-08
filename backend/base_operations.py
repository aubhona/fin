from query import get_base_data


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
