import os
import nothing
from flask import Flask, session, render_template, flash, redirect
from data import stdev_options, ema_options, Get_Raw
from Models import db, connect_db, Ticker, Operation
from forms import SimulationForm
from graphs import build_total_graph, build_ticker_graph, make_chart
import time


CURR_USER_KEY = "curr_user"

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', 'postgresql:///Bollinger'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "would a hacker guess this?")

connect_db(app)
db.create_all()


@app.route('/', methods=["GET","POST"])
def runSim():
    """main page where users start their simulation"""
    form = SimulationForm()

    if form.validate_on_submit():
        ticker = form.ticker.data.upper()
        EMA = form.EMAres.data
        sigma = form.STDmult.data
        #saves the form data in the session, then renders loading screen while processing
        session["sim"] = [ticker,EMA,sigma]
        
        if EMA not in ema_options:
            flash(f"invalid EMA resolution. Resolution must be an integer value between {ema_options[0]} and {ema_options[-1]}", "danger")

        if sigma not in stdev_options:
            flash(f"invalid EMA resolution. Resolution must be a number between {stdev_options[0]} and {stdev_options[-1]}", "danger")


        return redirect("/load")

    return render_template('Home.html', form_obj=form)
    

@app.route('/load', methods = ['GET'])
def loading_screen():
    """
    middle ground between running a sim and seeing results
    must include data in session
    """
    if "sim" in session:
        return render_template('loading.html')
    return redirect('/')


@app.route('/sim')
def sim_results():
    """
    shows the results for a custom simulation. 
    runs from the loading screen using data passed through the session
    can be accessed until a new sim is run or the browser is closed
    """
    if not "sim" in session:
        return redirect('/')
        
    ticker =  session["sim"][0]
    EMA = session["sim"][1]
    sigma = session["sim"][2]

    raw = Get_Raw(ticker, resolution='1d')
    try:
        chart = make_chart(raw,250,500)

    except:
        flash(f"No results for symbol: {ticker} try a symbol from the S&P 500", 'danger')
        return redirect('/')
        
    
    existing = Operation.query.filter((Operation.params == f"{EMA}X{sigma}"), (Operation.ticker_symbol == ticker)).one_or_none()
        
    if existing:
        relative_perf = round((existing.sim_performance - existing.buy_hold_performance) / (existing.buy_hold_performance)*100,2)  
        return render_template('strategy.html',results = existing, graph = chart, percent = relative_perf, param = [ticker,EMA,sigma])
    
    #try:
    results = Operation.run(ticker,EMA,sigma,raw)
    #except:
        #flash('Something went wrong. It is possible the stock you picked is not in the database, or does not have stored data for a long enough period', 'danger')
        #return redirect('/')
    db.session.add(results)
    db.session.commit()    

    relative_perf = round((results.sim_performance - results.buy_hold_performance) / (results.buy_hold_performance)*100,2) 
    return render_template("strategy.html",results = results, graph = chart, percent = relative_perf, param = [ticker,EMA,sigma])
    



@app.route('/results', methods=["GET", "POST"])
def show_all_results():
    """shows a chart of all results averaged for each strategy"""
    return  render_template('results.html', graph= build_total_graph())
  

@app.route('/info')
def info():
    """page with info about bollinger bands"""
    render_template('loading.html')
    return render_template('info.html')


@app.route('/tickers')
def list_tickers():
    """shows a table of stock symbols and their performance as an average"""
    all_tickers = Ticker.query.order_by(Ticker.symbol)
    return render_template('tickers.html', tickers = all_tickers)


@app.route('/tickers/<symbol>')
def ticker_performance(symbol):
    """shows the performance matrix of a single stock for the simulations that have been run"""
    ticker = Ticker.query.get_or_404(symbol)
    graph = build_ticker_graph(ticker)
    raw = Get_Raw(ticker.symbol,resolution='1mo')
    price_chart = make_chart(raw,270,1100)
    return render_template('single_ticker.html', ticker = ticker, graph = graph, price_chart=price_chart)


@app.route('/runAllSimulationsAndAddToDatabase')
def run_sims():
    """
    designed to be run once when app is implemented, 
    populates the results with a few common stocks over all strategies
    """

    stocks = ['TSLA','AAPL','NVDA','NFLX','AMZN','MSFT']

    for stock in stocks:
        raw = Get_Raw(stock)

        for i in stdev_options:
            for j in ema_options:
                existing = Operation.query.filter((Operation.params == f"{j}X{i}"),(Operation.ticker_symbol == stock)).one_or_none()
                if existing:
                    continue
                if not existing:
                    result = Operation.run(stock,j,i,raw)
                    db.session.add(result)
                    db.session.commit()
                    time.sleep(0.2)

    return redirect('/')
        