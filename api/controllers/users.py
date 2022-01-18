import sys
from db.models import users
from db.models import stocks

def validate_and_get_user(user):
    cash_cents = 0
    if user.get("cash_cents", None):
        cash_cents = user["cash_cents"]
        assert type(cash_cents) is int
        assert cash_cents >= 0
    user_model = users.Users(cash_cents)
    for stock in user.get("stocks", []):
        user_model.stocks.append(stocks.Stocks(stock["identifier"], stock["quantity"]))
    return user_model


def create_user(user, session):
    user_model = validate_and_get_user(user) # will raise if  validationerror
    session.add(user_model)
    session.commit()
    return user_model

def get_user(user_id, session):
    user = session.query(users.Users).filter(users.Users.id == user_id).first()
    return user.to_dict()

def get_users(session):
    all_users = session.query(users.Users).all()
    return list(map(lambda l: l.to_dict(), all_users))