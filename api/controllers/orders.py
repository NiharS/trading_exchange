from db.models import orders, users, stocks
from api.controllers import users as user_controller
from api.controllers import stocks as stock_controller

from sqlalchemy import func

def validate_and_get_order(order, user_id):
    # we require each of these parameters so just raise the not-found if we
    # don't get them
    stock_identifier = order.get("stock_identifier")
    price_cents = order.get("price_cents")
    quantity = order.get("quantity")
    is_sell = order.get("is_sell_order")
    order_model = orders.Orders(stock_identifier, quantity, price_cents, is_sell)
    order_model.user_id = user_id
    return order_model

def create_order(order, user_id, session):
    order_model = validate_and_get_order(order, user_id)
    user_model = (session
        .query(users.Users)
        .filter(users.Users.id == user_id)
        .first())
    stock_model = (session
        .query(stocks.Stocks)
        .filter(stocks.Stocks.user_id == user_id)
        .filter(stocks.Stocks.identifier == order_model.stock_identifier)
        .first())
    if order_model.is_sell_order:
        # check that we have enough of the stock to sell
        sellable_amount = stock_model.sellable_quantity
        if sellable_amount < order_model.quantity:
            raise Exception(f"attempting to sell {order_model.quantity} share(s) of {order_model.stock_identifier}, but only {sellable_amount} share(s) available to sell")
        stock_model.sellable_quantity -= order_model.quantity
    else:
        purchase_price = order_model.price_cents * order_model.quantity
        if purchase_price > user_model.liquid_cash:
            raise Exception("user does not have enough liquid cash to place this order")
        user_model.liquid_cash -= purchase_price
    session.add(order_model)
    session.commit()
    return order_model

def cancel_order(user_id, order_id, session):
    order = (session
        .query(orders.Orders)
        .filter(orders.Orders.id == order_id)
        .filter(orders.Orders.user_id == user_id)
        .first())
    if not order:
        raise Exception(f"order with id {order_id} not found for user {user_id}")
    user = (session
        .query(users.Users)
        .filter(users.Users.id == order.user_id)
        .first())
    # this might be None if we're buying a stock we don't own previously,
    # but we won't dereference this variable in that case
    stock = (session
        .query(stocks.Stocks)
        .filter(stocks.Stocks.user_id == order.user_id)
        .filter(stocks.Stocks.identifier == order.stock_identifier)
        .first())
    # If the order is complete, do nothing
    if order.remaining_quantity == 0:
        return
    # If the order has not had anything happen yet, delete it and adjust
    # the user's asset availability
    elif order.remaining_quantity == order.quantity:
        if order.is_sell_order:
            stock.sellable_quantity += order.quantity
        else:
            user.liquid_cash += order.quantity * order.price_cents
        order.delete()
    # And now for the fun part, if the order has been partially processed
    # then just drop the remaining amount, but keep the order around for posterity
    # (so the user can see all completed orders, including partially completed)
    else:
        if order.is_sell_order:
            stock.sellable_quantity += order.remaining_quantity
        else:
            user.liquid_cash += order.remaining_quantity * order.price_cents
        order.quantity -= order.remaining_quantity
        order.remaining_quantity = 0
    session.commit()
        

def get_user_orders(user_id, session, order_status="all"):
    user_orders = session.query(orders.Orders).filter(orders.Orders.user_id == user_id)
    if order_status == "completed":
        user_orders = user_orders.filter(orders.Orders.remaining_quantity == 0)
    elif order_status == "active":
        user_orders = user_orders.filter(orders.Orders.remaining_quantity > 0)
    results = user_orders.all()
    return list(map(lambda l: l.to_dict(), results))

def get_all_orders(order_status, session):
    all_orders = session.query(orders.Orders)
    if order_status == "completed":
        all_orders = all_orders.filter(orders.Orders.remaining_quantity == 0)
    elif order_status == "active":
        all_orders = all_orders.filter(orders.Orders.remaining_quantity > 0)
    results = all_orders.all()
    return list(map(lambda l: l.to_dict(), results))