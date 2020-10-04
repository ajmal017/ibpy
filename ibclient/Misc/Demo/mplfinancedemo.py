import pandas as pd
import mplfinance as mpf

df = pd.read_csv("yahoofinance-INTC-19950101-20040412.csv", index_col=0, parse_dates=True)

demonr = 2

if demonr == 1:
    mpf.plot(df, type='candle', style='charles',
                title='S&P 500, Nov 2019',
                ylabel='Price ($)',
                ylabel_lower='Shares \nTraded',
                volume=True,
                mav=(3,6,9),
                savefig='test-mplfiance.png')

elif demonr == 2:
    import matplotlib.pyplot as plt
    #from mplfinance import candlestick_ohlc
    from mplfinance.original_flavor import candlestick_ohlc
    import matplotlib.dates as mpdates
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

    # creating Subplots
    fig, ax = plt.subplots()

    df.drop('Adj Close', axis=1, inplace=True)
    df.reset_index(inplace=True)
    df.index.name = 'Date'
    df["Date"] = mpdates.date2num(df["Date"].values)
    cols = ['Date', 'Open', 'High', 'Low', 'Close']
    df = df[cols]

    df = df[['Date', 'Open', 'High',
             'Low', 'Close']]

    # plotting the data
    candlestick_ohlc(ax, df.values)

    # allow grid
    ax.grid(True)
    ah1=ax.axhline(y=3)
    ah1.set_label("jsdfds")
    ah=ax.hlines(y=5, xmin=9150, xmax=9700, label="strike")
    ah.axes.set_label("kj")
    ax.vlines(x=9150, ymin=2, ymax=8, lw=5, color='r', label="entry")

    # Setting labels
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')

    # setting title
    plt.title('Prices For the Period 01-07-2020 to 15-07-2020')

    # Formatting Date
    date_format = mpdates.DateFormatter('%d-%m-%Y')
    ax.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()

    fig.tight_layout()

    # show the plot
    plt.show()
    input("")
