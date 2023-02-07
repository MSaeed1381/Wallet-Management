from flask import jsonify
from app import app


@app.errorhandler(404)
def not_found_error():
    return jsonify({'error': 'not found'}), 404


@app.errorhandler(400)
def no_string_provided_error(string):
    return jsonify({'error': f'no {string} provided'}), 400


@app.errorhandler(400)
def string_already_exits(kind, string):
    return jsonify({"error": f"a {kind} with the given {string} already exists"}), 400


@app.errorhandler(400)
def invalid_error(name):
    return jsonify({"error": f"invalid {name}"}), 400


@app.errorhandler(400)
def wallet_not_contain_coin_error():
    return jsonify({"error": "the wallet does not contain the given coin"}), 400
