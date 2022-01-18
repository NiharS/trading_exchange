# This file will initialize the database with some sample data
import os
import requests

APP_HOST=os.environ.get("APP_HOST", "http://0.0.0.0")
APP_PORT=os.environ.get("APP_PORT", "5000")

exchange_users = [
    {
        "cash_cents": 100000,
        "stocks": [
            {
                "identifier": "GOOG",
                "quantity": 3
            }, {
                "identifier": "AAPL",
                "quantity": 5
            }, {
                "identifier": "AMZN",
                "quantity": 2
            }, 
        ]
    }, {
        "cash_cents": 50000,
        "stocks": [
            {
                "identifier": "GOOG",
                "quantity": 5
            }, {
                "identifier": "FB",
                "quantity": 1
            }, {
                "identifier": "MSFT",
                "quantity": 3
            }, {
                "identifier": "NVDA",
                "quantity": 7
            }
        ]
    }, {
        "cash_cents": 200000,
        "stocks": [
            {
                "identifier": "GOOG",
                "quantity": 3
            }, {
                "identifier": "ZM",
                "quantity": 20
            }, {
                "identifier": "TSLA",
                "quantity": 40
            }, {
                "identifier": "AMD",
                "quantity": 35
            }, 
        ]
    }, {
        "cash_cents": 1000000,
        "stocks": []
    }, {
        "cash_cents": 150000,
        "stocks": [
            {
                "identifier": "FB",
                "quantity": 7
            }
        ]
    }, {
        "cash_cents": 250000,
        "stocks": [
            {
                "identifier": "BRKA",
                "quantity": 2
            }, {
                "identifier": "GOOG",
                "quantity": 5
            }, 
        ]
    }, {
        "cash_cents": 123,
        "stocks": [
            {
                "identifier": "NVDA",
                "quantity": 9
            }, {
                "identifier": "FB",
                "quantity": 7
            }, {
                "identifier": "MSFT",
                "quantity": 3
            }, {
                "identifier": "GOOG",
                "quantity": 8
            }
        ]
    },
]

for user in exchange_users:
    res = requests.post(f"{APP_HOST}:{APP_PORT}/api/v1/users", json=user)
    print(res.text)