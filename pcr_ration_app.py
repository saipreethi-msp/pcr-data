import json
import requests
import pandas as pd
import time
from datetime import date, datetime
import streamlit as st
import pytz

# Function to fetch PCR data for the selected index
def fetch_data_and_calculate_pcr(index_symbol):
    # Fetch data from the URL
    url = f'https://www.nseindia.com/api/option-chain-indices?symbol={index_symbol}'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors
        
        data = json.loads(response.content.decode('utf-8'))

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
            'Time': datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M:%S %Z'),  # Adjust timezone here
            'Total Call': totCE,
            'Total Put': totPE,
            'PCR Ratio': PCR,
            'Nifty Value': spot_price,
            'Option Signal': option_signal
        }
        return pd.DataFrame([new_data])

    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

    # Return an empty DataFrame if an error occurs
    return pd.DataFrame()

# Function to get the appropriate index symbol based on user selection
def get_index_symbol(index_name):
    index_symbols = {
        'Nifty': 'NIFTY',
        'Nifty Bank': 'BANKNIFTY',
        'Nifty Financial Services': 'NIFTY_FIN_SERVICE',
        'Midcap': 'NIFTY_MIDCAP_50',
        'Sensex': 'SENSEX'
        # Add more indices as needed
    }
    return index_symbols.get(index_name, 'NIFTY')  # Default to Nifty if index_name not found

st.title('PCR Data Collection App')

# Select the index
selected_index = st.selectbox('Select an Index', ['Nifty', 'Nifty Bank', 'Nifty Financial Services', 'Midcap', 'Sensex'])

# Get the index symbol
index_symbol = get_index_symbol(selected_index)

# Button to trigger PCR display
if st.button('Show PCR Data'):
    # Set a key for the rerun
    if 'last_rerun' not in st.session_state:
        st.session_state['last_rerun'] = time.time()

    # Load and display the data
    if 'data' not in st.session_state or time.time() - st.session_state['last_rerun'] > 300:
        st.session_state['data'] = fetch_data_and_calculate_pcr(index_symbol)
        st.session_state['last_rerun'] = time.time()

    st.table(st.session_state['data'])
