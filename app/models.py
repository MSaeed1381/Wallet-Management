from datetime import datetime
from app import db


# TODO: Implement
class Wallet(db.Model):
    __tablename__ = 'wallets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    coins = db.relationship('WalletCoin', cascade='all,delete')

    def __repr__(self):
        return self.name


class Coin(db.Model):
    __tablename__ = 'coins'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True, unique=True, nullable=False)
    symbol = db.Column(db.String(255), index=True, unique=True, nullable=False)
    price = db.Column(db.Numeric, nullable=False)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    wallets = db.relationship('WalletCoin', cascade='all,delete')

    def __repr__(self):
        return self.name


class WalletCoin(db.Model):
    __tablename__ = 'wallet_coin'
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'))
    coin_id = db.Column(db.Integer, db.ForeignKey('coins.id'))
    quantity = db.Column(db.Numeric, nullable=False)

    coin = db.relationship('Coin', back_populates='wallets')
    wallet = db.relationship('Wallet', back_populates='coins')

    def __repr__(self):
        return "wallet coin " + str(id)

