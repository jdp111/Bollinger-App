import os
from flask import Flask, render_template, jsonify, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from data import run_Simulation, stdev_options, ema_options, Get_Raw
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

        raw = Get_Raw(ticker)
        if not raw:
            flash(f"No results for symbol: {ticker} try a symbol from the S&P 500", 'danger')
            return redirect('/')

        comparison, strat, buyHold, totalDays, strat_held = run_Simulation(raw,EMA,sigma)
        
        
        
        ticker_UD = Ticker.query.filter(Ticker.symbol == ticker).one_or_none()
        if not ticker_UD:
            ticker_UD = Ticker(symbol = ticker, stock_performance = comparison, weight = 1)
        else:
            ticker_UD.stock_performance = (ticker_UD.stock_performance* ticker_UD.weight + comparison)/(ticker_UD.weight +1)
            ticker_UD.weight +=1
            


        return redirect(f"/results/{simID}")

    return render_template('Home.html', form=form)
    

@app.route('/results/<strat_id>')
def single_result(strat_id):

    



@app.route('/results', methods=["GET", "POST"])
def signup():

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
    return render_template('info.html')

