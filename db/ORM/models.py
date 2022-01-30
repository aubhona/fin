from init_db import initdb

db = initdb("sqlite:///site.db")

class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    surname = db.Column(db.String, nullable = False)
    email = db.Column(db.String, nullable = False)
    login = db.Column(db.String, nullable = False)
    password = db.Column(db.Integer, nullable = False)
    
    def __init__(self, name, surname, email, login, password) -> None:
        self.name, self.surname, self.email, self.login, self.password = name, surname, email, login, hash(password)
    
    def __repr__(self) -> str:
        return f"{self.id}"

class Profits(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
    price = db.Column(db.Float, nullable = False)
    date = db.Column(db.String, nullable = False)
    user = db.relationship("Users", backref = db.backref("profits", lazy = False))
    
    def __init__(self, user_id, price, date) -> None:
        self.user_id, self.price, self.date = user_id, price, date

    def __repr__(self) -> str:
        return f"{self.id}"

class Expenses(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
    price = db.Column(db.Float, nullable = False)
    date = db.Column(db.String, nullable = False)
    cat = db.Column(db.String, nullable = False)
    user = db.relationship("Users", backref = db.backref("expenses", lazy = False))
    
    def __init__(self, user_id, price, date, cat) -> None:
        self.user_id, self.price, self.date, self.cat = user_id, price, date, cat

    def __repr__(self) -> str:
        return f"{self.id}"

