The purpose of this app is to show performance of Bollinger band trading strategy in short term trading on the stock market.
This app is currently deployed at https://bollinger-sim-app.herokuapp.com

How it Works:
Bollinger Bands
Bollinger bands were created by John Bollinger as a way to track fast movements in stock prices using the average and standard deviation. The bands themselves are calculations of the average over a given period (EMA resolution) plus or minus the standard deviation modified by some multiplier (σ).
The theory behind Bollinger Band trading strategies is that when a stock price drastically changes either high or low, it tends to pull back to the average elastically. The simplest version of this strategy is to buy stock when the price dips below the lower band, and sell when the price rises past the top band.
This website will uses a slightly more complicated version of this strategy. Our strategy marks when the price leaves the band (indicated in yellow on the graph above), then signals a buy or sell when it reenters as shown. Many variations on Bollinger band strategy have been suggested that make the strategy more effective and complicated, and later versions of this website may incorporate more compliacated versions.
Any short term trading strategy is inherently risky, and stock movements tend to be unpredictable. This app was created primarily to show risk, and help users make informed decisions about stock trading. This app is not intended to give financial advice, and I personally do not reccommend using simple Bollinger band trading as your primary trading strategy.

User Inputs
Ticker Symbol
The ticker symbol is a company-specific code used by the NYSE to keep track of stock prices. For the purposes of this app, the symbol indicates which stock to run a simulation on. Usually the symbol consists of a 2 to 4 letter designation (ex. Apple, inc. has the symbol 'AAPL'), but some can be longer or include other symbols. This app may not support certain ticker symbols, and while it should continue to be updated, if a company has been removed from the NYSE or changes symbols, the app may not understand some inputs.

EMA Resolution
This variable determines how many days are included in the calculations of the moving average and standard deviation. The moving average is a calculated average that changes every day to include the current day's price and all prices counting back the length of the EMA resolution. If this is difficult to understand, the simple explanation is that the higher the resolution number, the smoother the Bollinger bands will be, and the more often the price will go outside of them.

σ multiplier
σ, or standard deviation, is a measure of how different a group of numbers is from each other. Bollinger bands use this value to show a normal amount of travel in the stock price, so if the price travels outside, it is no longer within a normal deviation. The multiplier indicates how many standard deviations the Bollinger bands will be from the average. If this is difficult to understand, the simple explanation is that the higher the multiplier, the less the stock price will go outside the Bollinger bands.

Results Chart
The results chart shows the aggregate results from simulations run by all users. Each square on the chart represents the percentage return per year of that strategy, averaged over all instances run. When enough simulations are run that results become statistically significant, this chart will show which strategies perform best. Keep in mind when viewing this chart that the best result will be hilighted in green, whether or not the return is positive.
A similar version of this graph is available for individual stocks, which can be accessed through the "Stock Performance" tab. This shows how the individual stock performs over the range of strategies. different stocks will have different responses to any given strategy, and showing how they perform individually can help you create a better image in your mind of how performance trends are created.

App Flow:
The initial page of this app prompts users to create a custom Bollinger trading strategy. when a strategy is chosen, they are redirected to a results page for that strategy, which shows a few different metrics of performance. This page can only be reached by running a strategy, but if the strategy is run again, the results are taken from the database, so it can be retrieved quickly.
The performance of a custom simulation is added to the total results and averaged into the 'results' graph. the user can then look at the results of other strategies in the 'All Results' tab, or the results of individual stocks in the 'Stock Performance' tab.
The 'Stock Performance' tab shows a list of stocks, their performance, and simulations run. Users can access more information by clicking on a stock. This will show them a simple performance graph, and another strategy performance graph, similar to the performance graph for all strategies.

App Mechanics:
This app is made with Flask in Python, interfacing with HTML through Jinja, and the database through SQLAlchemy and PostgreSQL. The database stores performance information for stocks and performance information for individual simulations. Yfinance was used for stock market source data, and analysis on the data is performed by custom functions made by me. 

