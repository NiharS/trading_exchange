from db.models.stocks import Stocks

def validate_and_get_stock(stock):
    assert stock.get("identifier", "") != ""
    assert stock.get("quantity", 0) >= 0
    return Stocks(stock["identifier"], stock["quantity"])


def validate_and_get_stocks(stocks):
    all_stocks = []
    for stock in stocks:
        stock_model = validate_and_get_stock(stock)
        all_stocks.append(stock_model)
    return all_stocks

def get_for_user_and_identifier(user_id, identifier, session):
    return (session
        .query(Stocks)
        .filter(Stocks.user_id == user_id)
        .filter(Stocks.identifier == identifier)
        .first())
