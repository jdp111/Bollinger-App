import yfinance as yf
import pandas as pd
#from get_all_tickers import get_tickers as gt
import time
import numpy as np

timeRange = '10y'
resolution = '1d'
stdev_options = [0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,3.0]
ema_options = [25,24,23,22,21,20,19,18,17,16,15]

def Get_Raw(ticker):
    """
    returns data from a given ticker with options for
    .Open   --open price
    .Close  --close price
    .High   --daily high
    .Volume --trade volume
    .Dividends -- dividend paid
    [['Stock Splits']] -- stock split multiplier
    .index  --date
    """
    try:
        data =yf.Ticker(str(ticker)).history(period = timeRange, interval = resolution)
    except:
        return False
    return data


def STDev_calc(array,avg,mult):
    """
    calculates standard deviation and applies multiplier
    """
    S = 0
    for el in array:
        S += (el - avg) **2 / len(array)
    stdev = S**(.5)

    return stdev*mult


def get_price_data(EMAresolution,raw_data):
    """
    returns pandas object that contains all values necessary to determine price and gain
    when bought at open price
    """

    trunc_dates = raw_data.index[EMAresolution:].values.tolist()
    trunc_div   = raw_data.Dividends[EMAresolution:].values.tolist()
    trunc_split = raw_data[['Stock Splits']][EMAresolution:].values.tolist()
    print(len(trunc_dates))
    print(len(trunc_div))
    print(len(trunc_split))
    print(raw_data.Open[EMAresolution:])
    
    priceData = {'OpenPrice':raw_data.Open[EMAresolution:].values.tolist(),
                    'div' : trunc_div,
                    'split' : trunc_split,
                }
    

    df = pd.DataFrame(priceData, index = trunc_dates)
    #df.set_index([trunc_dates,'date'])
    return df


def get_decision_data(EMAresolution,raw_data,std_mult):
    """
    calculates the EMA over time of given closing price
    returns a pandas dataframe with all necessary data for running bollinger band strategy
    
    """
    #truncates the prices so the ema can calculate on the full range
    if len(raw_data.index) <= EMAresolution:
        return None


    trunc_range = range(EMAresolution,len(raw_data.index.values))
    trunc_dates = raw_data.index[EMAresolution:]

    #data required is EMA and stdev for decision making and div, split, and price for calculating buy, sell and gain prices
    decisionData = {
                 'ClosePrice' : raw_data.Close[EMAresolution:],
                 'EMA' : [],
                 'SellH':[],
                 'BuyL':[]
                 }

    for i in trunc_range:

        #this is the block of data analyzed for EMA and stdev with a length of EMAresolution
        #based on close because the stock will be bought on next open
        #calculated on i-1 because the strategy will activate on the day after trigger
        zone = raw_data.Close[(i-EMAresolution):i-1]

        currEMA = sum(zone)/len(zone)
        currSTDev = STDev_calc(zone,currEMA,std_mult)

        decisionData['EMA'].append(currEMA)
        decisionData['SellH'].append(currEMA+currSTDev)
        decisionData['BuyL'].append(currEMA-currSTDev)

    df = pd.DataFrame(decisionData,index = trunc_dates)

    return df



def run_Simulation(Raw_Data,EMAres,STD_Mult):
    price_data = get_price_data(EMAres,Raw_Data)
    graph_data = get_decision_data(EMAres,Raw_Data,STD_Mult)
    close = graph_data.ClosePrice
    highBol = graph_data.SellH
    lowBol = graph_data.BuyL
    holding = []
    stock_multiplier = 1
    total_days = 0
    performance = {"performance": 0, "days": 0 }   #units %/day
    buy_hold_perf = (close[-1]/close[0]-1) / len(close) # %/day
    
    for i in range(price_data):
        if close[i] < lowBol[i]:
            price = price_data.OpenPrice[i] * stock_multiplier
            bought_cond = (price,0, 0)
            holding.append(bought_cond)

        if close[i] > highBol[i]:
            sell_price = price_data.OpenPrice[i] * stock_multiplier

            for buy_price, divs, days in holding:
                Ret = (sell_price + divs)/buy_price - 1 # %
                #calculate the weighted average for total return
                weighted_perf = Ret + performance["performance"]*performance["days"]
                performance["days"] += days
                perf = weighted_perf/performance["days"]
                performance["performance"] = perf
        
        for buy_price, divs, days in holding:
            divs += price_data.div[i]
        
        if price_data.split[i]:
            stock_multiplier *= price_data.split[i]

        total_days +=1
    

    strat_perf = performance["performance"]
    relative_perf = ((strat_perf+1) - (buy_hold_perf+1))*100

    return (relative_perf,strat_perf,buy_hold_perf,total_days,performance["days"])

