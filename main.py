import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate

st.title('Stock Trading Strategy Backtesting App')

# Get user inputs
principal = st.number_input('Enter the principal amount:', value=10000.0)
symbol = st.text_input('Enter the stock symbol:')
start_date = st.date_input('Enter the start date:')
end_date = st.date_input('Enter the end date:')
strategy = st.selectbox('Select the trading strategy:', options=['SMA', 'EMA'])

if st.button('Run Backtest'):
    # Read data for the given stock symbol and date range
    data = pd.read_csv(f"/workspaces/magi_shit/PythonForFinance/13. Data Collection/Data/{symbol}.csv", parse_dates=['Date'], index_col='Date')
    data = data.loc[start_date:end_date]

    # Calculate moving averages and trading signals
    if strategy == 'SMA':
        data['20_SMA'] = data.Close.rolling(window=20, min_periods=1).mean()
        data['50_SMA'] = data.Close.rolling(window=50, min_periods=1).mean()
        data['Signal'] = np.where(data['20_SMA'] > data['50_SMA'], 1, 0)
    elif strategy == 'EMA':
        data['20_EMA'] = data.Close.ewm(span=20, adjust=False).mean()
        data['50_EMA'] = data.Close.ewm(span=50, adjust=False).mean()
        data['Signal'] = np.where(data['20_EMA'] > data['50_EMA'], 1, 0)
    else:
        st.warning('Invalid strategy selected!')
        st.stop()

    data['Position'] = data.Signal.diff()

    # Create plot
    fig, ax = plt.subplots(figsize=(20,10))
    data['Close'].plot(color = 'k', label= 'Close Price')
    if strategy == 'SMA':
        data['20_SMA'].plot(color = 'b',label = '20-day SMA')
        data['50_SMA'].plot(color = 'g', label = '50-day SMA')
    elif strategy == 'EMA':
        data['20_EMA'].plot(color = 'b',label = '20-day EMA')
        data['50_EMA'].plot(color = 'g', label = '50-day EMA')
    ax.plot(data[data['Position'] == 1].index, data['Close'][data['Position'] == 1], '^', markersize = 15, color = 'g', label = 'buy')
    ax.plot(data[data['Position'] == -1].index, data['Close'][data['Position'] == -1], 'v', markersize = 15, color = 'r', label = 'sell')
    ax.set_ylabel('Price in Rupees', fontsize = 15 )
    ax.set_xlabel('Date', fontsize = 15 )
    ax.set_title(f'{symbol.upper()} ({strategy.upper()} strategy, Principal = {principal})', fontsize = 20)
    ax.legend()
    ax.grid()
    st.pyplot(fig)

    # Create and print position table
    df_pos = data[(data['Position'] == 1) | (data['Position'] == -1)].copy()
    df_pos['Position'] = df_pos['Position'].apply(lambda x: 'Buy' if x==1 else 'Sell')
    df_pos.rename(columns={'Position': 'Action'}, inplace=True)
    df_pos.insert(0, 'Trade Date', df_pos.index)
    df_pos.reset_index(drop=True, inplace=True)
    df_pos['Quantity'] = principal / df_pos['Close']
    df_pos['Amount'] = df_pos['Quantity'] * df_pos['Close']
    df_pos['Cumulative Amount'] = df_pos['Amount'].cumsum()
    st.subheader('Position Table')
    st.table(df_pos[['Trade Date', 'Action', 'Close', 'Quantity', 'Amount', 'Cumulative Amount']].style.format({
    'Close': '{:.2f}',
    'Quantity': '{:.2f}',
    'Amount': '{:.2f}',
    'Cumulative Amount': '{:.2f}',
    }))

    # Print performance metrics
    st.write('## Performance Metrics')
    total_trades = len(df_pos)
    win_trades = len(df_pos[df_pos['Action']=='Sell'])
    loss_trades = total_trades - win_trades
    win_rate = win_trades/total_trades*100
    
    st.write(f'Total Trades: {total_trades}')
    st.write(f'Win Trades: {win_trades}')
    st.write(f'Loss Trades: {loss_trades}')
    st.write(f'Win Rate: {win_rate:.2f}%')

