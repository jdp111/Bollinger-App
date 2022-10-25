import plotly.express as px
import plotly.io as pio
import pandas as pd
from data import ema_options, stdev_options
from Models import Point, Operation


def build_total_graph():
    """
    builds graph of total results over all strats
    units of %/year of strategy
    """
    array = []
    for y in ema_options:
        row =[]
        for x in stdev_options:
            index = f"{y}X{x}"
            newPoint = Point.query.filter(Point.id == index).one_or_none()
            if newPoint:
                row.append(round(newPoint.strat_performance))
            else:
                row.append(None)
        array.append(row)
        
    data = array

    fig = px.imshow(data, 
                        labels=dict(x="σ Multiplier", y="EMA Resolution", color="performance (%/year)"),
                        x = [str(mult) for mult in stdev_options],
                        y = [str(res) for res in ema_options],
                        color_continuous_scale=[[0,'red'],[.5,'yellow'],[1,'green']]
                        )
    fig.layout.height = 700
    fig.layout.width = 1200

    return pio.to_html(fig,full_html=False)



def build_ticker_graph(ticker):
    """builds graph of all strategies for one ticker"""
    array = []
    for y in ema_options:
        row =[]
        for x in stdev_options:
            index = f"{y}X{x}"
            newPoint = Operation.query.filter((Operation.params==index),(Operation.ticker_symbol==ticker.symbol)).one_or_none()
            if newPoint:
                row.append(newPoint.sim_performance)
            else:
                row.append(None)
        array.append(row)
        
    data = array

    fig = px.imshow(data, 
                        labels=dict(x="σ Multiplier", y="EMA Resolution", color="performance (%/year)"),
                        x = [str(mult) for mult in stdev_options],
                        y = [str(res) for res in ema_options],
                        color_continuous_scale=[[0,'red'],[.5,'yellow'],[1,'green']]
                        )
    fig.layout.height = 700
    fig.layout.width = 1100

    return pio.to_html(fig,full_html=False)


def make_chart(raw, height, width):
    """
    shows a simple price chart for a ticker
    to be displayed on a single stock view
    """
    xdata = raw.index
    ydata = raw.Close
    df = pd.DataFrame({"Date" : xdata, "Price": ydata})
    
    fig = px.line(df, 
        x = "Date",
        y = "Price"
        )
    fig.layout.height = height
    fig.layout.width = width
    return pio.to_html(fig,full_html=False)