import yfinance as yf
import pandas as pd
import datetime

# Define the stock ticker and the moving average period
ticker = "AAPL"  # Example: Apple Inc.
n = 24  # Example: 50-day moving average
# Fetch historical stock data
start_date = (datetime.date.today()+datetime.timedelta(days=-n)).strftime('%Y-%m-%d')
end_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
stock_data = yf.download(ticker,start=start_date,end=end_date)


# Calculate the nth-period simple moving average (SMA)
stock_data['EMA'] = stock_data['Close'].ewm(span=n, adjust=False).mean()

# Display the data
print(stock_data[['EMA']])
