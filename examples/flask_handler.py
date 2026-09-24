from flask import Flask, jsonify, request

app = Flask(__name__)


@app.get("/orders/<int:order_id>")
def get_order(order_id: int):
    """Return an order as JSON, or 404 if it does not exist."""
    order = app.config["DB"].get_order(order_id)
    if order is None:
        return jsonify(error="not found"), 404
    if request.args.get("expand") == "items":
        order["items"] = app.config["DB"].get_items(order_id)
    return jsonify(order)
