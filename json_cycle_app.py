# Fetch JSON data from jsonplaceholder.typicode.com and display each item
# on a Streamlit app every 5 seconds
import streamlit as st
import pandas as pd
import requests
import time

# Get JSON from online source
response = requests.get('https://jsonplaceholder.typicode.com/posts')
json_data = response.json()

# Create Pandas DataFrame
df = pd.DataFrame(json_data)

# Streamlit header
st.header("Cycling Data Frame Every 5 Seconds!")

# Create empty Streamlit placeholder
placeholder = st.empty()

# Streamlit extra content
st.text("Daniel Chavez - Rebelway!")

# Populate the placeholder with a table
with placeholder.container():
    while True:
        for i in range(0, 4):
            idx = i % len(df)
            placeholder.table(df.iloc[idx])
            time.sleep(5)
