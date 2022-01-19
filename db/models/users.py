from sqlalchemy import BigInteger, Column, Integer
from sqlalchemy.orm import relationship
from . import stocks as stockModel
from . import Base

# The Users class represents the DB model for users.
# Each user has an ID, as well as some amount of cash.
# They have a "liquid" amount of cash, or cash available to invest. This is
# computed as their total cash minus the amount of cash allocated for pending
# buy-orders.
class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement="auto")
    # Cash is in number of cents (e.g. $100 is represented as 10000)
    # Some penny-stocks can cost fractional amounts of cents, but handling
    # exact precision for these stocks will likely result in significant floating-
    # point errors so as an easement I'm assuming orders will be for whole-number of
    # cents
    cash = Column(BigInteger, default=0)
    # Same here, represented in number of cents
    liquid_cash = Column(BigInteger, default=0)
    stocks = relationship("Stocks")

    def __init__(self, cash=0, stocks=[]):
        self.cash = cash
        self.liquid_cash = cash
        self.stocks = stocks

    def __repr__(self):
        return (
            f"{self.id}\n"
            + f"cash:{self.cash}, liquid={self.liquid_cash}\n"
            + "stocks:\n".join([f"  {stock}\n" for stock in self.stocks])
        )

    def to_dict(self):
        return {
            "id": self.id,
            "cash_cents": self.cash,
            "liquid_cash_cents": self.liquid_cash,
            "stocks": [stock.to_dict() for stock in self.stocks],
        }
