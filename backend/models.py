from app import db
from hashlib import md5

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    login = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    balance_exp = db.Column(db.Float, nullable=False)
    balance_prof = db.Column(db.Float, nullable=False)
    balance_tot = db.Column(db.Float, nullable=False)

    def __init__(self, name, surname, login, password) -> None:
        self.name, self.surname, self.login, self.password = name, surname, login, md5(password.encode('utf8')).hexdigest()
        self.balance_exp = 0
        self.balance_prof = 0
        self.balance_tot = 0

    def __repr__(self) -> str:
        return f"{self.id}"


class Profits(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.String, nullable=False)

    def __init__(self, user_id, price, date) -> None:
        self.user_id, self.price, self.date = user_id, price, date

    def __repr__(self) -> str:
        return f"{self.id}"


class Expenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.String, nullable=False)
    cat = db.Column(db.String, nullable=False)

    def __init__(self, user_id, price, date, cat) -> None:
        self.user_id, self.price, self.date, self.cat = user_id, price, date, cat

    def __repr__(self) -> str:
        return f"{self.id}"

db.create_all()