from sqlalchemy import BigInteger, Column, ForeignKey, Integer, Enum, Numeric, String
from . import Base

# The Stocks object represents a Stock held by a user
class Stocks(Base):
    __tablename__ = "stocks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    # Identifier to use when matching to other stocks of the same type (e.g. GOOG)
    identifier = Column(String)
    # How much of this stock do we own?
    # We could use Numeric here as with some securities, a user can have fractional amounts, and
    # Numeric has exact precision.
    # For the scope of this problem, though, we only have stock as a non-cash stock. We're
    # representing cash in number of cents, so to keep everything consistent I assume stock
    # is in units which cannot be fractional. Therefore I use a biginteger, as it may be possible
    # to exceed 4 bytes but I'm assuming that it's still an integer amount.
    quantity = Column(BigInteger)
    # How many are available to sell?
    sellable_quantity = Column(BigInteger)

    def __init__(self, stock_identifier, quantity):
        self.identifier = stock_identifier
        self.quantity = quantity
        self.sellable_quantity = quantity

    def __repr__(self):
        return f"id={self.id}, user_id={self.user_id}, identifier={self.identifier}, quantity={self.quantity}"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "identifier": self.identifier,
            "quantity": self.quantity,
            "sellable_quantity": self.sellable_quantity,
        }
