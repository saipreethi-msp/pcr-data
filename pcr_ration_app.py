import json
import requests
import pandas as pd
from datetime import datetime
import pytz
import streamlit as st
import time  # Ensure time is imported

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

    # Calculate PCR ratio
    PCR = totPE / totCE
    option_signal = 'Buy' if PCR > 1 else 'Sell' if PCR < 1 else 'Neutral'

    # Get current time in Indian Standard Time
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist)
    date_str = current_time.strftime('%Y-%m-%d')
    time_str = current_time.strftime('%H:%M:%S')

    # Append the data to a DataFrame
    new_data = {
        'Date': date_str,
        'Time': time_str,
        'PCR Ratio': PCR,
        'Option Signal': option_signal
    }
    return pd.DataFrame([new_data])

st.title('PCR Data Collection App')

# Load and display the data
if 'data' not in st.session_state or time.time() - st.session_state.get('last_run', 0) > 300:
    st.session_state['data'] = fetch_data_and_calculate_pcr()
    st.session_state['last_run'] = time.time()

st.table(st.session_state['data'])

# JavaScript to trigger a rerun every 300000 milliseconds (5 minutes)
st.markdown("""
    <script>
    setInterval(function() {
        window.location.reload();
    }, 300000);  // Reload page every 5 minutes
    </script>
""", unsafe_allow_html=True)
