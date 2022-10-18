"""SQLAlchemy models for Warbler."""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy


bcrypt = Bcrypt()
db = SQLAlchemy()


class Point(db.Model):
    """data point for graph of overall results"""
    __tablename__ = 'points'

    id = db.Column(db.String(7), primary_key=True)
    entry_count = db.Column(db.Integer)
    strat_performance = db.Column(db.Float, nullable=False)
    
class Ticker(db.Model):
    """shows the overall performance of a given stock"""
    __tablename__ = 'tickers'

    symbol = db.Column(db.String(6), primary_key = True)
    stock_performance = db.Column(db.Float)
    weight = db.Column(db.Integer)


class Operation(db.Model):
    """stores simulations run by all users, relates points to tickers"""
    __tablename__= 'operations'

    id = db.Column(db.Integer,primary_key = True, autoincrement=True,)
    params = db.Column(db.String,db.ForeignKey('points.id',ondelete="cascade"))
    ticker_symbol = db.Column(db.String,db.ForeignKey('tickers.symbol',ondelete="cascade"))
    sim_performance = db.Column(db.Float, nullable=False )

def connect_db(app):
    """Connect this database to provided Flask app.
    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)  