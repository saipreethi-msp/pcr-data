import json
import requests
import pandas as pd
import time
from datetime import date
import streamlit as st

def fetch_data_and_calculate_pcr():
    # Fetch data from the URL
    url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9'
    }
    response = requests.get(url, headers=headers).content
    data = json.loads(response.decode('utf-8'))

    # Extract relevant data
    totCE = data['filtered']['CE']['totOI']
    totPE = data['filtered']['PE']['totOI']
    spot_price = data['records']['data'][0]['PE']['underlyingValue']

    # Calculate PCR ratio
    PCR = totPE / totCE
    option_signal = 'Buy' if PCR > 1 else 'Sell' if PCR < 1 else 'Neutral'

    # Append the data to a DataFrame
    new_data = {
        'Date': date.today().isoformat(),
        'Time': time.strftime('%H:%M:%S'),
        'PCR Ratio': PCR,
        'Total Call': [totCE],
        'Total Put': [totPE],
        'PCR Ratio': [PCR],
        'LTP': [spot_price], 
        'Option Signal': option_signal
    }
    return pd.DataFrame([new_data])

st.title('PCR Data Collection App')

# Set a key for the rerun
if 'last_rerun' not in st.session_state:
    st.session_state['last_rerun'] = time.time()

# Load and display the data
if 'data' not in st.session_state or time.time() - st.session_state['last_rerun'] > 300:
    st.session_state['data'] = fetch_data_and_calculate_pcr()
    st.session_state['last_rerun'] = time.time()
    st.experimental_rerun()

st.table(st.session_state['data'])
