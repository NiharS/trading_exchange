FROM python:3.9

ENV FLASK_APP=server

COPY ./api/requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

WORKDIR /code

COPY server.py server.py
COPY db /code/db
COPY trading_queue /code/trading_queue
COPY api /code/api

CMD [ "flask", "run", "--host=0.0.0.0" ]