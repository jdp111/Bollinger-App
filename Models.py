from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from data import run_Simulation


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
    buy_hold_performance = db.Column(db.Float)


class Operation(db.Model):
    """stores simulations run by all users, relates points to tickers"""
    __tablename__= 'operations'

    id = db.Column(db.Integer,primary_key = True, autoincrement=True,)  
    params = db.Column(db.String,db.ForeignKey('points.id',ondelete="cascade"))             ## EMAXSD
    ticker_symbol = db.Column(db.String,db.ForeignKey('tickers.symbol',ondelete="cascade")) ## TSLA
    sim_performance = db.Column(db.Float)                                                   ## %/year
    buy_hold_performance = db.Column(db.Float) 
    sim_days = db.Column(db.Integer)
    total_days = db.Column(db.Integer)


    @classmethod
    def run(cls,ticker,EMA,sigma,raw):
        """ adds a method when it is run by user"""

        strat, buyHold, totalDays, strat_held = run_Simulation(raw,EMA,sigma)
        
        point = Point.query.get(f"{EMA}X{sigma}")

        if not point:
            point = Point(id = f"{EMA}X{sigma}", entry_count = 1, strat_performance=strat)
            db.session.add(point)

        else:
            point.strat_performance = (point.strat_performance * point.entry_count + strat)/(point.entry_count + 1)
            point.entry_count +=1

        #this part updates the information for the given stock and measures aggregate response
        ticker_UD = Ticker.query.filter(Ticker.symbol == ticker).one_or_none()
        if not ticker_UD:
            ticker_UD = Ticker(symbol = ticker, stock_performance = strat, weight = 1)
            db.session.add(ticker_UD)
            
        else:            
            ticker_UD.stock_performance = round((ticker_UD.stock_performance* ticker_UD.weight + strat)/(ticker_UD.weight+1),2)
            ticker_UD.weight +=1

        ticker_UD.buy_hold_performance = buyHold #%/year
        db.session.commit()

        sim = Operation(
            params = f"{EMA}X{sigma}",
            ticker_symbol = ticker,
            sim_performance = strat,
            buy_hold_performance = buyHold,
            sim_days = strat_held,
            total_days = totalDays
            )
        
        return sim


def connect_db(app):
    """Connect this database to provided Flask app.
    You should call this in your Flask app.
    """
    db.app = app
    db.init_app(app)  