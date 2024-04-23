import json
import requests
import pandas as pd
import time
from datetime import date
import streamlit as st

def fetch_data_and_calculate_pcr(index_symbol):
    # URL to fetch data from
    url = f'https://www.nseindia.com/api/option-chain-indices?symbol={index_symbol}'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9'
    }

    try:
        # Attempt to get a response from the API
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = json.loads(response.content.decode('utf-8'))

        # Extract relevant data
        totCE = data['filtered']['CE']['totOI']
        totPE = data['filtered']['PE']['totOI']

        # Calculate PCR ratio
        PCR = totPE / totCE
        option_signal = 'Buy' if PCR > 1 else 'Sell' if PCR < 1 else 'Neutral'

        # Append the data to a DataFrame
        new_data = {
            'Date': date.today().isoformat(),
            'Time': time.strftime('%H:%M:%S'),
            'PCR Ratio': PCR,
            'Option Signal': option_signal
        }
        return pd.DataFrame([new_data])

    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

    # Return an empty DataFrame in case of an error
    return pd.DataFrame()

st.title('PCR Data Collection App')

selected_index = st.selectbox('Select an Index', ['Nifty', 'Nifty Bank', 'Nifty Financial Services', 'Midcap', 'Sensex'])
index_symbol = get_index_symbol(selected_index)

if 'last_rerun' not in st.session_state:
    st.session_state['last_rerun'] = time.time()

if 'data' not in st.session_state or time.time() - st.session_state['last_rerun'] > 300:
    st.session_state['data'] = fetch_data_and_calculate_pcr(index_symbol)
    st.session_state['last_rerun'] = time.time()
    st.rerun()

st.table(st.session_state['data'])
