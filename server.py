import json
import sys
from db import Session
from flask import Flask, request
from trading_queue import queue
import api.controllers.users as user_controller
import api.controllers.orders as order_controller

app = Flask(__name__)
queue_conn = queue.create_connection()

@app.route("/alive")
def check_liveness():
    return {}, 200

# The application endpoints all create a DB session as the lazy-loaded models
# need a Session for validating their values. So we create a session for each
# and pass the session to the controller code.

@app.route("/api/v1/users", methods=["POST"])
def create_user():
    with Session() as session:
        body = request.get_json(force=True)
        try:
            user = user_controller.create_user(body, session)
            return user.to_dict(), 201
        except Exception as e:
            return {
                "error": str(e),
            }, 500

@app.route("/api/v1/users", methods=["GET"])
def get_users():
    with Session() as session:
        try:
            return json.dumps(user_controller.get_users(session)), 200
        except Exception as e:
            return {
                "error": str(e),
            }, 500

@app.route("/api/v1/users/<user_id>", methods=["GET"])
def get_user(user_id):
    with Session() as session:
        try:
            return json.dumps(user_controller.get_user(user_id, session)), 200
        except Exception as e:
            return {
                "error": str(e),
            }, 500

# For query parameters, can do status=completed,active,all
@app.route("/api/v1/users/<user_id>/orders", methods=["GET"])
def get_user_orders(user_id):
    args = request.args
    order_status = args.get("status", "all")
    with Session() as session:
        try:
            return json.dumps(order_controller.get_user_orders(user_id, session, order_status)), 200
        except Exception as e:
            return {
                "error": str(e),
            }, 500

@app.route("/api/v1/users/<user_id>/orders", methods=["POST"])
def create_user_order(user_id):
    body = request.get_json(force=True)
    with Session() as session:
        try:
            order = order_controller.create_order(body, user_id, session)
            channel = queue.create_trading_channel(queue_conn)
            queue.send_on_channel(str(order.id), channel)
            return order.to_dict(), 201
        except Exception as e:
            return {
                "error": str(e),
            }, 500


@app.route("/api/v1/orders", methods=["GET"])
def get_all_orders():
    args = request.args
    order_status = args.get("status", "all")
    with Session() as session:
        try:
            return json.dumps(order_controller.get_all_orders(order_status, session)), 200
        except Exception as e:
            return {
                "error": str(e),
            }, 500

@app.route("/api/v1/users/<user_id>/orders/<order_id>", methods=["DELETE"])
def cancel_order(user_id, order_id):
    with Session() as session:
        try:
            order_controller.cancel_order(user_id, order_id, session)
            return {}, 200
        except Exception as e:
            return {
                "error": str(e),
            }, 500