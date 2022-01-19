from http import server
from time import time, timezone
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    DateTime,
)
from . import Base
from sqlalchemy.sql import func


class Orders(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, autoincrement="auto")
    user_id = Column(Integer, ForeignKey("users.id"))

    # The identifier of the stock to be traded
    stock_identifier = Column(String)

    # The amount of the stock to be traded
    quantity = Column(BigInteger)

    # The amount of the stock remaining to be traded (after any partial trade
    # completions)
    remaining_quantity = Column(BigInteger)

    # The price to trade each share of the stock at
    price_cents = Column(Integer)

    # Is this a buy or sell order?
    is_sell_order = Column(Boolean, default=True)

    # When was this order created?
    created_ts = Column(DateTime(timezone=False), server_default=func.now())

    def __init__(self, stock_identifier, quantity, price_cents, is_sell_order):
        self.stock_identifier = stock_identifier
        self.quantity = quantity
        self.remaining_quantity = quantity
        self.price_cents = price_cents
        self.is_sell_order = is_sell_order

    def repr(self):
        return f"id={self.id}, user_id={self.user_id}, stock={self.stock_identifier}, quantity = {self.quantity}, remaining_quantity={self.remaining_quantity}, price={self.price_cents}"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "stock": self.stock_identifier,
            "quantity": self.quantity,
            "remaining_quantity": self.remaining_quantity,
            "price_cents": self.price_cents,
            "created_at": self.created_ts.isoformat(),
        }
