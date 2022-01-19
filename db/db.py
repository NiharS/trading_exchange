import os
import sys
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# import each model so they're registered with the Base
from db.models.users import Users
from db.models.stocks import Stocks
from db.models.orders import Orders
from db.models import Base

DB_URL = os.environ.get("DB_URL", "postgres")
retries = 10
time_between_retries = 5
while retries > 0:
    try:
        engine = create_engine(
            f"postgresql+psycopg2://postgres:password@{DB_URL}:5432/trading_exchange"
        )
        Base.metadata.create_all(bind=engine)
        break
    except Exception as e:
        print("db not ready, waiting and retrying", file=sys.stderr)
        retries -= 1
        time.sleep(time_between_retries)
if retries == 0:
    sys.exit(1)
Session = sessionmaker(bind=engine)
