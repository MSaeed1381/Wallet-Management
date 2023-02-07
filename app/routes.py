from flask import request, jsonify
from app import app, db
from app.models import *
from app.errors import *


def get_coins_from_wallet(wallet):
    coins = []
    for wallet_coin in wallet.coins:
        coins.append((Coin.query.filter_by(id=wallet_coin.coin_id).first(), wallet_coin.quantity))
    return coins


def get_balance(wallet):
    balance = 0

    for coin in get_coins_from_wallet(wallet):
        balance += coin[0].price * coin[1]
    return balance


def get_coins_dictionary(wallet):
    coins = []
    for coin in get_coins_from_wallet(wallet):
        coin = coin[0]
        wallet_coin = WalletCoin.query.filter_by(wallet_id=wallet.id, coin_id=coin.id).first()
        coins.append({
            "id": coin.id,
            "name": coin.name,
            "symbol": coin.symbol,
            "price": coin.price,
            "quantity": wallet_coin.quantity,
            "created_at": coin.created_at,
            "updated_at": coin.updated_at
        })
    return coins


def get_wallet_dictionary(wallet):
    return {
        "id": wallet.id,
        "name": wallet.name,
        "balance": get_balance(wallet),
        "coins": get_coins_dictionary(wallet),
        "created_at": wallet.created_at,
        "updated_at": wallet.updated_at
    }


def get_coin_dictionary(coin):
    return {
            "id": coin.id,
            "name": coin.name,
            "symbol": coin.symbol,
            "price": coin.price,
            "created_at": coin.created_at,
            "updated_at": coin.updated_at
            }


@app.route('/wallets', methods=['GET'])
def get_wallets_information():
    wallets = Wallet.query.all()
    result = []
    for wallet in wallets:
        result.append(get_wallet_dictionary(wallet))
    return jsonify(result), 200


@app.route('/wallets', methods=['POST'])
def create_wallets():
    name = request.form.get('name')
    if name is None:
        return no_string_provided_error('name')

    if Wallet.query.filter_by(name=name).first() is not None:
        return string_already_exits('wallet', 'name')

    wallet = Wallet(name=name)
    db.session.add(wallet)
    db.session.commit()
    wallet = Wallet.query.filter_by(name=name).first()
    return jsonify(get_wallet_dictionary(wallet)), 201


@app.route('/wallets/<int:wallet_id>', methods=['PUT'])
def edit_wallet(wallet_id):
    wallet = Wallet.query.filter_by(id=wallet_id).first()
    if wallet is None:
        return not_found_error()

    name = request.form.get('name')
    if name is None:
        return no_string_provided_error('name')

    wallet = Wallet.query.filter_by(name=name).first()
    if wallet is not None:
        return string_already_exits('wallet', 'name')

    wallet = Wallet.query.filter_by(id=wallet_id).first()
    wallet.updated_at = datetime.utcnow()
    wallet.name = name
    db.session.commit()
    return get_wallet_dictionary(wallet), 200


@app.route('/wallets/<int:wallet_id>', methods=['DELETE'])
def delete_wallet(wallet_id):
    wallet = Wallet.query.filter_by(id=wallet_id).first()
    if wallet is None:
        return not_found_error()

    db.session.delete(wallet)
    db.session.commit()
    return get_wallet_dictionary(wallet)


@app.route('/coins', methods=['GET'])
def get_coins():
    coins = Coin.query.all()
    result = []
    for coin in coins:
        result.append(get_coin_dictionary(coin))
    return jsonify(result), 200


@app.route('/coins', methods=['POST'])
def create_coin():
    name = request.form.get('name')
    if name is None:
        return no_string_provided_error('name')

    symbol = request.form.get('symbol')
    if symbol is None:
        return no_string_provided_error('symbol')

    price = request.form.get('price')
    if price is None:
        return no_string_provided_error('price')

    if Coin.query.filter_by(name=name).first() is not None:
        return string_already_exits('coin', 'name')

    if Coin.query.filter_by(symbol=symbol).first() is not None:
        return string_already_exits('coin', 'symbol')

    coin = Coin(name=name, symbol=symbol, price=price)
    db.session.add(coin)
    db.session.commit()
    return jsonify(get_coin_dictionary(coin)), 201


@app.route('/wallets/<int:wallet_id>/add_coin', methods=['POST'])
def add_coin_to_wallet(wallet_id):
    wallet = Wallet.query.filter_by(id=wallet_id).first()
    if wallet is None:
        return not_found_error()

    coin_id = request.form.get('coin_id')
    if coin_id is None:
        return no_string_provided_error('coin_id')

    coin = Coin.query.filter_by(id=coin_id).first()
    if coin is None:
        return invalid_error('coin_id')

    quantity = request.form.get('quantity')

    if quantity is None:
        return no_string_provided_error('quantity')

    wallet_coin = WalletCoin.query.filter_by(coin_id=coin_id, wallet_id=wallet_id).first()
    if wallet_coin is None:
        wallet_coin = WalletCoin(coin_id=coin_id, wallet_id=wallet_id, quantity=quantity)
        db.session.add(wallet_coin)
    else:
        wallet_coin.quantity = quantity
    wallet.updated_at = datetime.utcnow()
    db.session.commit()
    return get_wallet_dictionary(wallet), 200


@app.route('/wallets/<int:wallet_id>/delete_coin', methods=['DELETE'])
def delete_coin_from_wallet(wallet_id):
    wallet = Wallet.query.filter_by(id=wallet_id).first()
    if wallet is None:
        return not_found_error()

    coin_id = request.form.get('coin_id')
    if coin_id is None:
        return no_string_provided_error('coin_id')

    coin = Coin.query.filter_by(id=coin_id).first()
    if coin is None:
        return invalid_error('coin_id')

    wallet_coin = WalletCoin.query.filter_by(coin_id=coin_id, wallet_id=wallet_id).first()
    if wallet_coin is None:
        return wallet_not_contain_coin_error()

    db.session.delete(wallet_coin)
    wallet.updated_at = datetime.utcnow()
    db.session.commit()
    return get_wallets_information()


@app.route('/coins/<int:coin_id>', methods=['DELETE'])
def delete_coin(coin_id):
    coin = Coin.query.filter_by(id=coin_id).first()
    if coin is None:
        return not_found_error()

    db.session.delete(coin)
    db.session.commit()
    return jsonify(get_coin_dictionary(coin)), 200


@app.route('/coins/<int:coin_id>', methods=['PUT'])
def edit_coin(coin_id):
    coin = Coin.query.filter_by(id=coin_id).first()
    if coin is None:
        return not_found_error()

    name = request.form.get('name')
    if name is None:
        return no_string_provided_error('name')

    symbol = request.form.get('symbol')
    if symbol is None:
        return no_string_provided_error('symbol')

    price = request.form.get('price')
    if price is None:
        return no_string_provided_error('price')

    coin = Coin.query.filter_by(name=name).first()
    if coin is not None and coin.id != coin_id:
        return string_already_exits('coin', 'name')

    coin = Coin.query.filter_by(symbol=symbol).first()
    if coin is not None and coin.id != coin_id:
        return string_already_exits('coin', 'symbol')

    coin = Coin.query.filter_by(id=coin_id).first()
    coin.updated_at = datetime.utcnow()
    coin.name = name
    coin.price = price
    coin.symbol = symbol
    db.session.commit()
    return jsonify(get_coin_dictionary(coin)), 200
