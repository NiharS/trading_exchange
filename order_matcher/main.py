import sys
from trading_queue import queue
from db.models import orders, users, stocks
from db import Session

connection = queue.create_connection()

def get_matching_order(session, order, exclude=set()):
    order_query = (session.
        query(orders.Orders).
        # match the stock name
        filter(orders.Orders.stock_identifier == order.stock_identifier).
        # only incomplete orders
        filter(orders.Orders.remaining_quantity > 0).
        # don't allow a user to match their own order
        filter(orders.Orders.user_id != order.user_id).
        # exclude orders we've already seen
        filter(orders.Orders.id.notin_(exclude)))
    if order.is_sell_order:
        order_query = (order_query.
            # search for a buy order
            filter(orders.Orders.is_sell_order == False).
            # only consider buyers with prices higher than your sell price
            filter(orders.Orders.price_cents >= order.price_cents).
            # if I'm selling, I want the highest buy price possible. After that, older orders first
            order_by(orders.Orders.price_cents.desc(), orders.Orders.created_ts.asc()))
    else:
        order_query = (order_query.
            # search for a sell order
            filter(orders.Orders.is_sell_order == True).
            # only consider sellers with selling prices less than what you want
            # to buy it for
            filter(orders.Orders.price_cents <= order.price_cents).
            # If I'm buying, I don't care which order I match with, my price is fixed. Take the oldest
            order_by(orders.Orders.created_ts.asc()))

    return order_query.first()

def update_stock_for_sale(session, seller_id, stock_identifier, quantity):
    stock = (session
        .query(stocks.Stocks)
        .filter(stocks.Stocks.identifier == stock_identifier)
        .filter(stocks.Stocks.user_id == seller_id)
        .first())
    # sellable quantity should already be correct
    stock.quantity -= quantity
    session.commit()

def update_stock_for_purchase(session, buyer_id, stock_identifier, quantity):
    stock = (session
        .query(stocks.Stocks)
        .filter(stocks.Stocks.identifier == stock_identifier)
        .filter(stocks.Stocks.user_id == buyer_id)
        .first())
    stock.quantity += quantity
    stock.sellable_quantity += quantity
    session.commit()

def handle_order(ch, method, properties, body):
    order_id = int(body)
    with Session() as session:
        order = session.query(orders.Orders).filter(orders.Orders.id == order_id).first()
        order_creator = session.query(users.Users).filter(users.Users.id == order.user_id).first()
        if not order or order.remaining_quantity == 0:
            return
        matches = set()
        matching_order = get_matching_order(session, order)
        while matching_order and order.remaining_quantity > 0:
            matching_user = session.query(users.Users).filter(users.Users.id == matching_order.user_id).first()
            seller, buyer = order_creator, matching_user
            if not order.is_sell_order:
                seller, buyer = matching_user, order_creator
            # the amount of shares that overlap
            match_amount = min(matching_order.remaining_quantity, order.remaining_quantity)
            # price of the transfer per share (will be the buy order's price)
            price_per_share = max(matching_order.price_cents, order.price_cents)
            # decrease each order by the amount traded
            matching_order.remaining_quantity -= match_amount
            order.remaining_quantity -= match_amount
            # give the seller the cash, and let them use it
            seller.cash += price_per_share * match_amount
            seller.liquid_cash += price_per_share * match_amount
            # scope down the buyers cash (purchase price already factored into liquid cash)
            buyer.cash -= price_per_share * match_amount
            # move the shares
            update_stock_for_purchase(session, buyer.id, order.stock_identifier, match_amount)
            update_stock_for_sale(session, seller.id, order.stock_identifier, match_amount)
            # just to be safe, commit what we've done so far before continuing
            session.commit()

            # fetch another order
            matches.add(matching_order.id)
            matching_order = get_matching_order(session, order, exclude=matches)
                            
queue.create_trading_consumer(connection, handle_order)
