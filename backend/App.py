from flask import Flask, jsonify
from flask_cors import CORS
import joblib

import yfinance as yf
import pandas as pd

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import date, timedelta

import os

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(__file__)

APPLE_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'training','models','AAPL.pkl')
AMAZON_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'training','models','AMZN.pkl')
MICROSOFT_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'training','models','MSFT.pkl')
NVIDIA_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'training','models','NVDA.pkl')

with open(APPLE_MODEL_PATH,'rb') as f:
    apple = joblib.load(f)
    
with open(AMAZON_MODEL_PATH,'rb') as f:
    amazon = joblib.load(f)

with open(MICROSOFT_MODEL_PATH,'rb') as f:
    microsoft = joblib.load(f)

with open(NVIDIA_MODEL_PATH,'rb') as f:
    nvidia = joblib.load(f)

def set_periodic_variables():
    window = 14
    short_period = 12
    long_period = 26
    signal_line_period = 9
    
    return window, short_period, long_period, signal_line_period

def date_now():
    today = str(date.today() - timedelta(days=2))
    return today

def load_overall_dataset():
    today = date_now()
    df_apple = yf.download("AAPL", start="2020-01-01", end=today)
    df_microsoft = yf.download("MSFT", start="2020-01-01", end=today)
    df_amazon = yf.download("AMZN", start="2020-01-01", end=today)
    df_nvidia = yf.download("NVDA", start="2020-01-01", end=today)

    # Flatten multi-level columns produced by newer yfinance versions
    for df in [df_apple, df_microsoft, df_amazon, df_nvidia]:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

    # Reset index so Date becomes a normal column
    df_apple = df_apple.reset_index()
    df_microsoft = df_microsoft.reset_index()
    df_amazon = df_amazon.reset_index()
    df_nvidia = df_nvidia.reset_index()

    if any(d.empty for d in [df_apple, df_microsoft, df_amazon, df_nvidia]):
        raise ValueError("One or more yfinance downloads returned empty data. Try again later.")

    return df_apple, df_microsoft, df_amazon, df_nvidia

def load_dataset(ticker="", company=""):
    date_today = date_now()
    df = yf.download(ticker, start="2020-01-01", end=date_today)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index()

    if df.empty:
        raise ValueError(f"yfinance returned empty data for {ticker}. Try again later.")

    return df

def convert_type(df):
    df['Close'] = df['Close'].astype(float)
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    df['Open'] = df['Open'].astype(float)
    df['Volume'] = df['Volume'].astype(int)
    df['Date'] = pd.to_datetime(df['Date'])

def engineer_features(df, window, short_period, long_period, signal_line_period):
    df['Price Change'] = df['Close'].diff().fillna(0)
    
    df['Gain'] = df.loc[df['Price Change'] > 0, 'Price Change']
    df['Loss'] = -df.loc[df['Price Change'] < 0, 'Price Change']
    df['Gain'] = df['Gain'].fillna(0)
    df['Loss'] = df['Loss'].fillna(0)
    
    df['Average Gain'] = df['Gain'].rolling(window=window).mean().fillna(0)
    df['Average Loss'] = df['Loss'].rolling(window=window).mean().fillna(0)
    
    df['RS'] = df['Average Gain'] / df['Average Loss']
    df['RSI'] = 100 - (100 / (1 + df['RS']))
    
    df['Short EMA'] = df['Close'].ewm(span=short_period,adjust=False).mean()
    df['Long EMA'] = df['Close'].ewm(span=long_period, adjust=False).mean()
    
    df['MACD'] = df['Short EMA'] - df['Long EMA']
    df['Signal Line'] = df['MACD'].ewm(span=signal_line_period, adjust=False).mean()
    df['MACD Histogram'] = df['MACD'] - df['Signal Line']
    return df

def drop_features_and_na(df):
    df = df.drop(columns=['Gain', 'Loss'])
    df = df.dropna()
    return df

#NEEDS SOME CHANGES ON FILE PATH BEFORE DEPLOYING ESPECIALLY ON savefig() function
def print_all_plots(datas, stock, labels):
    for i in range(len(datas)):
        plt.figure(figsize=(10.5,3.5))
        sns.lineplot(data=datas[i], x='Date', y='Close', errorbar=None)
        sns.despine()
        plt.xlabel(xlabel="")
        plt.ylabel(ylabel="")
        plt.savefig(f"../frontend/public/svg_visuals/{stock}_{labels[i]}.svg")
        plt.close()
        
        #Sub chart
        plt.figure(figsize=(10.5,3.5))
        sns.lineplot(data=datas[i], x='Date', y='Close', errorbar=None)
        sns.despine()
        plt.xlabel(xlabel="")
        plt.ylabel(ylabel="")
        plt.savefig(f"../frontend/public/svg_visuals/{stock}_{labels[i]}_m.svg")
        plt.close()
        
        plt.figure(figsize=(16.2,3.5))
        sns.lineplot(data=datas[i], x='Date', y='RSI', errorbar=None)
        sns.despine()
        plt.xlabel(xlabel="")
        plt.ylabel(ylabel="")
        plt.savefig(f"../frontend/public/svg_visuals/{stock}_{labels[i]}_m_RSI.svg")
        plt.close()
        
        fig = px.line(data_frame=datas[i], x='Date', y='Close')
        fig.update_layout(width=1520, 
                          height=660,
                          xaxis_title='', 
                          yaxis_title='',
                          margin=dict(l=0,r=0,t=0,b=0))
        fig.write_html(f"../frontend/public/chart_visuals/{stock}_{labels[i]}.html")


TICKER_MAP = {
    'apple': 'AAPL',
    'amazon': 'AMZN',
    'microsoft': 'MSFT',
    'nvidia': 'NVDA',
}

TIME_MAP = {
    'week': 7,
    'month': 31,
    'year': 365,
    'alltime': None,  # all time = full dataset
}

@app.route('/plot/window/<stock>/<time>')
def plot_window(stock, time):
    from flask import send_file
    import io

    ticker = TICKER_MAP.get(stock.lower())
    if not ticker:
        return jsonify({'error': f'Unknown stock: {stock}'}), 404

    days = TIME_MAP.get(time.lower())
    if time.lower() not in TIME_MAP:
        return jsonify({'error': f'Unknown time window: {time}'}), 404

    window, short_period, long_period, signal_line_period = set_periodic_variables()

    df = load_dataset(ticker=ticker, company=stock.lower())
    convert_type(df)
    df = engineer_features(df, window, short_period, long_period, signal_line_period)
    df = drop_features_and_na(df)

    if days is not None:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        df = df.loc[(df['Date'] <= pd.to_datetime(end_date)) & (df['Date'] > pd.to_datetime(start_date))]

    fig, ax = plt.subplots(figsize=(10.5, 3.5))
    sns.lineplot(data=df, x='Date', y='Close', ax=ax, errorbar=None)
    sns.despine(ax=ax)
    ax.set_xlabel('')
    ax.set_ylabel('')
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)

    return send_file(buf, mimetype='image/png')


@app.route('/chart/plotly/<stock>/<time>')
def chart_plotly(stock, time):
    from flask import make_response

    ticker = TICKER_MAP.get(stock.lower())
    if not ticker:
        return jsonify({'error': f'Unknown stock: {stock}'}), 404

    if time.lower() not in TIME_MAP:
        return jsonify({'error': f'Unknown time window: {time}'}), 404

    days = TIME_MAP.get(time.lower())
    window, short_period, long_period, signal_line_period = set_periodic_variables()

    df = load_dataset(ticker=ticker, company=stock.lower())
    convert_type(df)
    df = engineer_features(df, window, short_period, long_period, signal_line_period)
    df = drop_features_and_na(df)

    if days is not None:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        df = df.loc[(df['Date'] <= pd.to_datetime(end_date)) & (df['Date'] > pd.to_datetime(start_date))]

    fig = px.line(data_frame=df, x='Date', y='Close', title=f'{ticker} Stock Price')
    fig.update_layout(
        width=None,
        height=None,
        autosize=True,
        xaxis_title='',
        yaxis_title='Price (USD)',
        margin=dict(l=40, r=20, t=40, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )

    html_str = fig.to_html(full_html=True, include_plotlyjs='cdn')
    response = make_response(html_str)
    response.headers['Content-Type'] = 'text/html'
    return response




"""
TODO: 
    gains/loss getter, 
    open/close price getter,
    high/low price getter,
    main plot getter,
    overview plot getter,
    rsi plot getter
"""

@app.route('/analyze')
def analyze():
    df_apple, df_microsoft, df_amazon, df_nvidia = load_overall_dataset()

    dfs = [df_apple, df_amazon, df_microsoft, df_nvidia]
    window, short_period, long_period, signal_line_period = set_periodic_variables()
    stocks = ['AAPL', 'AMZN', 'MSFT', 'NVDA']

    for i, df in enumerate(dfs):
        convert_type(df)
        df = engineer_features(df, window, short_period, long_period, signal_line_period)
        df = drop_features_and_na(df)

    return jsonify({'status': 'ok', 'message': 'Analysis complete'})
        
        
@app.route('/stocks/apple')
def apple_analyze():
    df_apple = load_dataset(ticker='AAPL', company='apple')
    
    window, short_period, long_period, signal_line_period = set_periodic_variables()
    convert_type(df_apple)
    df_apple = engineer_features(df_apple, window, short_period, long_period, signal_line_period)
    df_apple = drop_features_and_na(df_apple)
    
    week_start_date = date.today() - timedelta(days=7)
    month_start_date = date.today() - timedelta(days=31)
    year_start_date = date.today() - timedelta(days=365)
    all_start_date = date.today() - timedelta(days=len(df_apple))
    end_date = date.today()
    
    week = df_apple.loc[(df_apple['Date'] <= pd.to_datetime(end_date)) & (df_apple['Date'] > pd.to_datetime(week_start_date))]
    month = df_apple.loc[(df_apple['Date'] <= pd.to_datetime(end_date)) & (df_apple['Date'] > pd.to_datetime(month_start_date))]
    year = df_apple.loc[(df_apple['Date'] <= pd.to_datetime(end_date)) & (df_apple['Date'] > pd.to_datetime(year_start_date))]
    all_time = df_apple.loc[(df_apple['Date'] <= pd.to_datetime(end_date)) & (df_apple['Date'] > pd.to_datetime(all_start_date))]
    
    week_price_change = week.loc[:,'Price Change'].sum()
    month_price_change = month.loc[:,'Price Change'].sum()
    year_price_change = year.loc[:,'Price Change'].sum()
    all_price_change = all_time.loc[:,'Price Change'].sum()
    
    week_price_high = week.loc[:,'High'].max()
    month_price_high = month.loc[:,'High'].max()
    year_price_high = year.loc[:,'High'].max()
    all_price_high = all_time.loc[:,'High'].max()
    
    week_price_low = week.loc[:,'Low'].min()
    month_price_low = month.loc[:,'Low'].min()
    year_price_low = year.loc[:,'Low'].min()
    all_price_low = all_time.loc[:,'Low'].min()

    latest_feature = all_time.drop(columns=['Close','Date']).iloc[-1]
    latest_features = latest_feature.values.reshape(1, -1)
    
    prediction = apple.predict(latest_features)
    
    return jsonify({'ticker':'AAPL',
                    'weekly change': round(week_price_change, 2), 
                    'monthly change': round(month_price_change, 2),
                    'yearly change': round(year_price_change, 2),
                    'all change': round(all_price_change, 2),
                    'weekly high': round(week_price_high, 2),
                    'monthly high': round(month_price_high, 2),
                    'yearly high': round(year_price_high, 2),
                    'all high': round(all_price_high, 2),
                    'weekly low': round(week_price_low, 2),
                    'monthly low': round(month_price_low, 2),
                    'yearly low': round(year_price_low, 2),
                    'all low': round(all_price_low, 2),
                    'predicted price': round(prediction[0], 2)})
    
@app.route('/stocks/amazon')
def amazon_analyze():
    df_amazon = load_dataset(ticker='AMZN', company='amazon')
    
    window, short_period, long_period, signal_line_period = set_periodic_variables()
    convert_type(df_amazon)
    df_amazon = engineer_features(df_amazon, window, short_period, long_period, signal_line_period)
    df_amazon = drop_features_and_na(df_amazon)
    
    week_start_date = date.today() - timedelta(days=7)
    month_start_date = date.today() - timedelta(days=31)
    year_start_date = date.today() - timedelta(days=365)
    all_start_date = date.today() - timedelta(days=len(df_amazon))
    end_date = date.today()
    
    week = df_amazon.loc[(df_amazon['Date'] <= pd.to_datetime(end_date)) & (df_amazon['Date'] > pd.to_datetime(week_start_date))]
    month = df_amazon.loc[(df_amazon['Date'] <= pd.to_datetime(end_date)) & (df_amazon['Date'] > pd.to_datetime(month_start_date))]
    year = df_amazon.loc[(df_amazon['Date'] <= pd.to_datetime(end_date)) & (df_amazon['Date'] > pd.to_datetime(year_start_date))]
    all_time = df_amazon.loc[(df_amazon['Date'] <= pd.to_datetime(end_date)) & (df_amazon['Date'] > pd.to_datetime(all_start_date))]
    
    week_price_change = week.loc[:,'Price Change'].sum()
    month_price_change = month.loc[:,'Price Change'].sum()
    year_price_change = year.loc[:,'Price Change'].sum()
    all_price_change = all_time.loc[:,'Price Change'].sum()
    
    week_price_high = week.loc[:,'High'].max()
    month_price_high = month.loc[:,'High'].max()
    year_price_high = year.loc[:,'High'].max()
    all_price_high = all_time.loc[:,'High'].max()
    
    week_price_low = week.loc[:,'Low'].min()
    month_price_low = month.loc[:,'Low'].min()
    year_price_low = year.loc[:,'Low'].min()
    all_price_low = all_time.loc[:,'Low'].min()
    
    latest_feature = all_time.drop(columns=['Close','Date']).iloc[-1]
    latest_features = latest_feature.values.reshape(1, -1)
    
    prediction = apple.predict(latest_features)
    
    return jsonify({'ticker':'AMZN',
                    'weekly change': round(week_price_change, 2), 
                    'monthly change': round(month_price_change, 2),
                    'yearly change': round(year_price_change, 2),
                    'all change': round(all_price_change, 2),
                    'weekly high': round(week_price_high, 2),
                    'monthly high': round(month_price_high, 2),
                    'yearly high': round(year_price_high, 2),
                    'all high': round(all_price_high, 2),
                    'weekly low': round(week_price_low, 2),
                    'monthly low': round(month_price_low, 2),
                    'yearly low': round(year_price_low, 2),
                    'all low': round(all_price_low, 2),
                    'predicted price': round(prediction[0], 2)})
    
@app.route('/stocks/microsoft')
def microsoft_analyze():
    df_microsoft = load_dataset(ticker='MSFT', company='microsoft')
    
    window, short_period, long_period, signal_line_period = set_periodic_variables()
    convert_type(df_microsoft)
    df_microsoft = engineer_features(df_microsoft, window, short_period, long_period, signal_line_period)
    df_microsoft = drop_features_and_na(df_microsoft)
    
    week_start_date = date.today() - timedelta(days=7)
    month_start_date = date.today() - timedelta(days=31)
    year_start_date = date.today() - timedelta(days=365)
    all_start_date = date.today() - timedelta(days=len(df_microsoft))
    end_date = date.today()
    
    week = df_microsoft.loc[(df_microsoft['Date'] <= pd.to_datetime(end_date)) & (df_microsoft['Date'] > pd.to_datetime(week_start_date))]
    month = df_microsoft.loc[(df_microsoft['Date'] <= pd.to_datetime(end_date)) & (df_microsoft['Date'] > pd.to_datetime(month_start_date))]
    year = df_microsoft.loc[(df_microsoft['Date'] <= pd.to_datetime(end_date)) & (df_microsoft['Date'] > pd.to_datetime(year_start_date))]
    all_time = df_microsoft.loc[(df_microsoft['Date'] <= pd.to_datetime(end_date)) & (df_microsoft['Date'] > pd.to_datetime(all_start_date))]
    
    week_price_change = week.loc[:,'Price Change'].sum()
    month_price_change = month.loc[:,'Price Change'].sum()
    year_price_change = year.loc[:,'Price Change'].sum()
    all_price_change = all_time.loc[:,'Price Change'].sum()
    
    week_price_high = week.loc[:,'High'].max()
    month_price_high = month.loc[:,'High'].max()
    year_price_high = year.loc[:,'High'].max()
    all_price_high = all_time.loc[:,'High'].max()
    
    week_price_low = week.loc[:,'Low'].min()
    month_price_low = month.loc[:,'Low'].min()
    year_price_low = year.loc[:,'Low'].min()
    all_price_low = all_time.loc[:,'Low'].min()
    
    latest_feature = all_time.drop(columns=['Close','Date']).iloc[-1]
    latest_features = latest_feature.values.reshape(1, -1)
    
    prediction = apple.predict(latest_features)
    
    return jsonify({'ticker':'MSFT',
                    'weekly change': round(week_price_change, 2), 
                    'monthly change': round(month_price_change, 2),
                    'yearly change': round(year_price_change, 2),
                    'all change': round(all_price_change, 2),
                    'weekly high': round(week_price_high, 2),
                    'monthly high': round(month_price_high, 2),
                    'yearly high': round(year_price_high, 2),
                    'all high': round(all_price_high, 2),
                    'weekly low': round(week_price_low, 2),
                    'monthly low': round(month_price_low, 2),
                    'yearly low': round(year_price_low, 2),
                    'all low': round(all_price_low, 2),
                    'predicted price': round(prediction[0], 2)})

@app.route('/stocks/nvidia')
def nvidia_analyze():
    df_nvidia = load_dataset(ticker='NVDA', company='nvidia')
    
    window, short_period, long_period, signal_line_period = set_periodic_variables()
    convert_type(df_nvidia)
    df_nvidia = engineer_features(df_nvidia, window, short_period, long_period, signal_line_period)
    df_nvidia = drop_features_and_na(df_nvidia)
    
    week_start_date = date.today() - timedelta(days=7)
    month_start_date = date.today() - timedelta(days=31)
    year_start_date = date.today() - timedelta(days=365)
    all_start_date = date.today() - timedelta(days=len(df_nvidia))
    end_date = date.today()
    
    week = df_nvidia.loc[(df_nvidia['Date'] <= pd.to_datetime(end_date)) & (df_nvidia['Date'] > pd.to_datetime(week_start_date))]
    month = df_nvidia.loc[(df_nvidia['Date'] <= pd.to_datetime(end_date)) & (df_nvidia['Date'] > pd.to_datetime(month_start_date))]
    year = df_nvidia.loc[(df_nvidia['Date'] <= pd.to_datetime(end_date)) & (df_nvidia['Date'] > pd.to_datetime(year_start_date))]
    all_time = df_nvidia.loc[(df_nvidia['Date'] <= pd.to_datetime(end_date)) & (df_nvidia['Date'] > pd.to_datetime(all_start_date))]
    
    week_price_change = week.loc[:,'Price Change'].sum()
    month_price_change = month.loc[:,'Price Change'].sum()
    year_price_change = year.loc[:,'Price Change'].sum()
    all_price_change = all_time.loc[:,'Price Change'].sum()
    
    week_price_high = week.loc[:,'High'].max()
    month_price_high = month.loc[:,'High'].max()
    year_price_high = year.loc[:,'High'].max()
    all_price_high = all_time.loc[:,'High'].max()
    
    week_price_low = week.loc[:,'Low'].min()
    month_price_low = month.loc[:,'Low'].min()
    year_price_low = year.loc[:,'Low'].min()
    all_price_low = all_time.loc[:,'Low'].min()
    
    latest_feature = all_time.drop(columns=['Close','Date']).iloc[-1]
    latest_features = latest_feature.values.reshape(1, -1)
    
    prediction = apple.predict(latest_features)
    
    return jsonify({'ticker':'NVDA',
                    'weekly change': round(week_price_change, 2), 
                    'monthly change': round(month_price_change, 2),
                    'yearly change': round(year_price_change, 2),
                    'all change': round(all_price_change, 2),
                    'weekly high': round(week_price_high, 2),
                    'monthly high': round(month_price_high, 2),
                    'yearly high': round(year_price_high, 2),
                    'all high': round(all_price_high, 2),
                    'weekly low': round(week_price_low, 2),
                    'monthly low': round(month_price_low, 2),
                    'yearly low': round(year_price_low, 2),
                    'all low': round(all_price_low, 2),
                    'predicted price': round(prediction[0], 2)})

if __name__ == '__main__':
    port = int(os.environ.get("Port", 5000))
    app.run(host="0.0.0.0",port=port)


