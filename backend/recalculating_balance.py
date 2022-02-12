from fin.backend.query import get_balance
import requests
import json


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
