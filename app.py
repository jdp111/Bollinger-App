import os
from flask import Flask, Response, session, render_template, jsonify, request, flash, redirect
from flask_debugtoolbar import DebugToolbarExtension
from data import run_Simulation, stdev_options, ema_options, Get_Raw, make_chart
from Models import db, connect_db, Point, Ticker, Operation
from forms import SimulationForm
import plotly.express as px
import plotly.io as pio

#from forms import 
#from models import

CURR_USER_KEY = "curr_user"

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', 'postgresql:///Bollinger'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)
db.drop_all()
db.create_all()

def build_graph():
    array = []
    for y in ema_options:
        row =[]
        for x in stdev_options:
            index = f"{x}X{y}"
            newPoint = Point.query.filter(Point.id == index).one_or_none()
            row.append(newPoint)
        array.append(row)
        
    return array


@app.route('/', methods=["GET","POST"])
def runSim():
    """main page where users start their simulation"""
    form = SimulationForm()

    if form.validate_on_submit():
        ticker = form.ticker.data
        EMA = form.EMAres.data
        sigma = form.STDmult.data
        #saves the form data in the session, then renders loading screen while processing
        session["sim"] = [ticker,EMA,sigma]
        return redirect("/load")

    return render_template('Home.html', form_obj=form)
    

@app.route('/load', methods = ['GET'])
def loading_screen():
    if "sim" in session:
        return render_template('loading.html')
    return redirect('/')

@app.route('/sim')
def sim_results():
    if not "sim" in session:
        return redirect('/')
        
    ticker =  session["sim"][0]
    EMA = session["sim"][1]
    sigma = session["sim"][2]

    raw = Get_Raw(ticker)
    try:
        chart = make_chart(raw)

    except:
        flash(f"No results for symbol: {ticker} try a symbol from the S&P 500", 'danger')
        return redirect('/')
        
    
    existing = Operation.query.filter((Operation.params == f"{EMA}X{sigma}") & (Operation.ticker_symbol == ticker)).one_or_none()
        
    if existing:
        return render_template('strategy.html',results = existing, chart = chart)

    results = Operation.run(ticker,EMA,sigma,raw)

    db.session.add(results)
    db.session.commit()    
    return render_template("strategy.html",results = results, graph = chart)
    



@app.route('/results', methods=["GET", "POST"])
def show_all_results():
    """shows a chart of all results averaged for each strategy"""

    data = build_graph()
    data[0][0]=4
    fig = px.imshow(data, 
                    labels=dict(x="σ Multiplier", y="EMA Resolution", color="performance (%)"),
                    x = [str(mult) for mult in stdev_options],
                    y = [str(res) for res in ema_options],
                    color_continuous_scale=[[0,'red'],[.5,'yellow'],[1,'green']]
                    )
    fig.layout.height = 700
    fig.layout.width = 1200

    return  render_template('results.html', graph= pio.to_html(fig,full_html=False))
  
@app.route('/info')
def info():
    render_template('loading.html')
    return render_template('info.html')



