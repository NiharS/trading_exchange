FROM python:3.9

COPY ./order_matcher/requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

WORKDIR /code

COPY db /code/db
COPY order_matcher/main.py /code/main.py
COPY trading_queue /code/trading_queue

CMD ["python", "main.py"]