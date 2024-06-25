from typing import Tuple

from custom_exceptions import FetchError, InputValidationError, InsertionError
from flask import Flask, Response, jsonify, request
from logger_setup import setup_logger
from repository import PostgreSQLShipmentRepository

app = Flask(__name__)

logger = setup_logger()

shipment_repo = PostgreSQLShipmentRepository()


@app.route("/shipments/", methods=["POST"])
def create_shipments() -> Tuple[Response, int]:
    data = request.json
    if not data:
        logger.error("No data provided on %s %s" % (request.method, request.endpoint))
        return jsonify({"error": "No data provided"}), 400

    try:
        shipment_repo.insert_shipments(data)
    except InputValidationError as e:
        logger.error("Invalid data format or missing required fields on %s %s" % (request.method, request.endpoint))
        return jsonify({"error": "Invalid data format or missing required fields", "details": str(e)}), 400
    except InsertionError as e:
        logger.error("Insertion error on %s %s" % (request.method, request.endpoint))
        return jsonify({"error": "Insertion error", "details": str(e)}), 500

    logger.info("Shipments created successfully on %s %s" % (request.method, request.endpoint))
    return jsonify({"message": "Shipments created successfully"}), 201


@app.route("/shipments/", methods=["GET"])
def get_shipments() -> Tuple[Response, int]:
    request_params = request.args.to_dict()
    if not all(elem in ["carrier", "date", "price"] for elem in request_params.keys()):
        logger.error("Malformed query params on %s %s" % (request.method, request.endpoint))
        return jsonify({"error": "Malformed query params"}), 400

    try:
        results = shipment_repo.fetch_shipments(request_params)
    except FetchError as e:
        logger.error("Fetch error on %s %s" % (request.method, request.endpoint))
        return jsonify({"error": "Fetch error", "details": str(e)}), 500

    logger.error("Shipments fetched successfully on %s %s" % (request.method, request.endpoint))
    return jsonify([dict(row) for row in results]), 200
