import yfinance as yf
import pandas as pd
import datetime
import matplotlib.pyplot as plt


def tommorowYF():
   return (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

def todayYF():
   return datetime.date.today().strftime('%Y-%m-%d')

def datesFromPeriod(period):
   start_date = (datetime.date.today() - datetime.timedelta(days=period)).strftime('%Y-%m-%d')
   end_date = todayYF()
   return start_date, end_date

def getNthPeriodEMA(period, data):
   return data.ewm(span=period, adjust=False).mean()
   
#start_date=todayYF(), end_date=datesFromPeriod(50)[1]

def customMACD(data, short_period=12, long_period=26, signal_period=9):
   short_ema = getNthPeriodEMA(short_period, data)
   long_ema = getNthPeriodEMA(long_period, data)
   macd = short_ema - long_ema
   signal = getNthPeriodEMA(signal_period, macd)
   histogram = macd - signal
   return macd, signal, histogram
   
def MoCS(tickers, end_date=todayYF(), start_date=datesFromPeriod(50)[1], short_period=12, long_period=26, signal_period=9):
   data = yf.download(tickers, period='3mo')
   differences = data['Close'][tickers[0]] / data['Close'][tickers[1]]
   #print(differences)
   macd, signal, histogram = customMACD(differences, short_period, long_period, signal_period)
   key = tickers[0] + 'vs' + tickers[1]
   data[key + '_MoCS'] = macd
   data[key + '_Signal'] = signal
   data[key + '_Histogram'] = histogram
   return key, data

def positiveOrNegativeSince(data):
   since = data.index[-1]
   sign = data.loc[data.index[-1]] > 0
   for i in range(len(data)-1, -1, -1):
      if data.index[i] != data.index[-1] and (data.loc[data.index[i]] > 0) != sign:
         since = data.index[i]
         break
   return sign, since


tickers = ["VOO", "AAPL" , "MSFT","GOOGL","TSLA","AMZN", "META", "JPM", "NVDA", "AMD", "V", "LMT", "DELL", "SNOW", "GME", "AMC"]
#tickers = ["VOO", "AAPL"]
MoCSMatrix = pd.DataFrame(columns=tickers, index=tickers)

for i, ticker1 in enumerate(tickers):
   momentum = {}
   sign = {}
   for j, ticker2 in enumerate(tickers):
      if ticker1 != ticker2:
         key, data = MoCS([ticker1, ticker2])
         signSince = positiveOrNegativeSince(data[key+'_MoCS'])
         momentumSince = positiveOrNegativeSince(data[key+'_Histogram'])
         if(signSince[0] == True):
            sign[0] = "Positive"
            sign[1] = signSince[1].strftime('%m/%d')
         else:
            sign[0] = "Negative"
            sign[1] = signSince[1].strftime('%m/%d')

         if(sign[0] == "Negative"):
            if(momentumSince[0] == True):
               momentum[0] = "Decelerating"
               momentum[1] = momentumSince[1].strftime('%m/%d')
            else:
               momentum[0] = "Accelerating"
               momentum[1] = momentumSince[1].strftime('%m/%d')
         else:
            if(momentumSince[0] == True):
               momentum[0] = "Accelerating"
               momentum[1] = momentumSince[1].strftime('%m/%d')
            else:
               momentum[0] = "Decelerating"
               momentum[1] = momentumSince[1].strftime('%m/%d')

         MoCSMatrix.loc[ticker1, ticker2] = key + ":" + sign[0] + " since " + sign[1] + " and " + momentum[0] + " since " + momentum[1]
      else:
         MoCSMatrix.loc[ticker1, ticker2] = "N/A"

def highlight_cell(x):
   if isinstance(x, float):
      return ''
   if "Positive" in x and "Accelerating" in x:
      return 'background-color: green'
   if "Positive" in x and "Decelerating" in x:
      return 'background-color: yellow'
   if "Negative" in x and "Accelerating" in x:
      return 'background-color: red'
   if "Negative" in x and "Decelerating" in x:
      return 'background-color: orange'

styled_MoCSMatrix = MoCSMatrix.style.applymap(highlight_cell)
styled_MoCSMatrix.to_excel('MoCSMatrixsmall.xlsx', engine='openpyxl')
today_data = data.loc[data.index[-1]]
print(key)
print("Today Data")
print(today_data[key+'_MoCS'], today_data[key+'_Signal'], today_data[key+'_Histogram'])
print("Past Data")
print(data[key+'_MoCS'], data[key+'_Signal'], data[key+'_Histogram'])

plt.title(key)
plt.plot(data[key+'_MoCS'], label='MoCS')
plt.plot(data[key+'_Signal'], label='Signal')
plt.legend()
plt.show()


