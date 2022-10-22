import yfinance as yf
import pandas as pd
#from get_all_tickers import get_tickers as gt
import time
import numpy as np

timeRange = 'max'
resolution = '1d'
stdev_options = [0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0]
ema_options = [24,23,22,21,20,19,18,17,16,15,14,13,12,11,10]

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
    time.sleep(1)
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

    trunc_dates = raw_data.index.values.tolist()[EMAresolution:]

    #some stocks do not have dividends. this function changes dividends to zero if excepts
    try:
        trunc_div   = raw_data.Dividends.values.tolist()[EMAresolution:]
    except:
        trunc_div = np.zeros(len(trunc_dates))
    
    #some stocks do not have splits. this function changes splits to zero if excepts
    try:
        trunc_split = raw_data['Stock Splits'].values.tolist()[EMAresolution:]
    except:
        trunc_split = np.zeros(len(trunc_dates))

    open = raw_data.Open.values.tolist()[EMAresolution:]
    priceData = {'OpenPrice': open,
                    'Div' : trunc_div,
                    'split' : trunc_split
                }
    

    df = pd.DataFrame(priceData, index = trunc_dates)
    return df


def get_decision_data(EMAresolution,raw_data,std_mult):
    """
    calculates the EMA over time of given closing price
    returns a pandas dataframe with all necessary data for running bollinger band strategy
    
    """
    #truncates the prices so the ema can calculate on the full range
    if len(raw_data.index) <= 365:
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
        #add 1 because the endpoints on indexing are inclusive
        zone = raw_data.Close[(i+1-EMAresolution):i]

        currEMA = sum(zone)/len(zone)
        currSTDev = STDev_calc(zone,currEMA,std_mult)

        decisionData['EMA'].append(currEMA)
        decisionData['SellH'].append(currEMA+currSTDev)
        decisionData['BuyL'].append(currEMA-currSTDev)

    df = pd.DataFrame(decisionData,index = trunc_dates)

    return df




def run_Simulation(Raw_Data,EMAres,STD_Mult):
    price_data = get_price_data(EMAres,Raw_Data) # Close, EMA, BollH, BollL
    graph_data = get_decision_data(EMAres,Raw_Data,STD_Mult) # Open, divs, splits
    close = graph_data.ClosePrice.values
    highBol = graph_data.SellH.values
    lowBol = graph_data.BuyL.values
    open = price_data.OpenPrice.values
    div = price_data.Div.values
    split = price_data.split.values

    holding = []
    stock_multiplier = 1
    total_days = len(price_data.index)
    #total performance
    performance = {"performance": 0, "days": 0 }   #units %/day, days
    
    total_divs = 0
    #these variables keep track of where the price is (higher or lower than the band region)
    low = False  #the price will begin inside the band region
    high = False

    for i in range(1,len(price_data.index)):

        # calculate at close[i-1] because stocks are bought the day after buy signals
        # these 2 if statements will never trigger on the same run
        if close[i-1] < lowBol[i-1]: #price falls low outside the band region     
            low = True               #price shows outside
        if close[i-1] >= lowBol[i-1] and low: #determine buy signal, triggers when price falls back into band region
            low = False
            buy_price = open[i] * stock_multiplier   #buy stock
            bought_cond = [buy_price,0, 0]   #saves two variables for addition of dividends and days held
            holding.append(bought_cond)  #collects open stock positions

        # these 2 if statements will never trigger on the same run
        if close[i-1] > highBol[i-1]: #price falls high outside the band region
            high = True
        if close[i-1] <= highBol[i-1] and high:#determine sell signal
            high = False
            for buy_div_days in holding: # run sale on all open positions
                buy = buy_div_days[0]
                days = buy_div_days[2]

                sell = open[i] * stock_multiplier + buy_div_days[1]  # $ amount @sell
                Ret_rate = round(np.log(sell/buy)/days,3) *100  # %/day return based on the formula Pf/Pi = exp(r*t) where r is rate of increase
                #calculate the weighted average for total return
                #weights return on stock by days held, and total performance by total days held
                weighted_perf = Ret_rate*days + performance["performance"]*performance["days"]  # %
                performance["days"] += days           #adds to total days
                performance["performance"] = weighted_perf/performance["days"]  # %/day averages return over whole period
                
            holding = []  # when the stocks in "holding" are sold, the array is cleared for new stocks

        for holds in holding:
            holds[1] += div[i]   # adds any div amount to all open positions
            holds[2] += 1        # progresses day count for open positions
        
        if split[i]:
            stock_multiplier *= split[i] # contributes a split if one happens

        total_divs += div[i]
    
    
    

    BH_endprice = close[-1] * stock_multiplier + total_divs
    buy_hold_perf =   round(np.log(BH_endprice/close[0])/total_days,3 )*100  # %/day return based on the formula Pf/Pi = exp(r*t) where r is rate of increase
    
    #this function to prevent division by 0
    if np.absolute(buy_hold_perf) < .00000001:
            buy_hold_perf = .00000001

    strat_perf =   performance["performance"] # %/day total strategy performance per day
    strat_held =   performance["days"]
    relative_perf = round((strat_perf - buy_hold_perf) / buy_hold_perf ,3)*100  # % difference in performance of the strategy

    # if the strategy performs infinitely better, it must be limited
    if relative_perf > 400:
        relative_perf = 400

    if relative_perf < -400:
        relative_perf = -400
    
    return relative_perf,strat_perf,buy_hold_perf,total_days,strat_held


