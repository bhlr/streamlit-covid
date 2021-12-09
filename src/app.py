import streamlit as st
import pandas as pd
import numpy as np

st.title('Uber pickups in NYC')

st.markdown('The dashboard will visualize the Covid-19 Situation in India')
st.markdown('Coronavirus disease (COVID-19) is an infectious disease caused by a newly discovered coronavirus. Most people infected with the COVID-19 virus will experience mild to moderate respiratory illness and recover without requiring special treatment.')
st.sidebar.title("Visualization Selector")
st.sidebar.markdown("Select the Charts/Plots accordingly:")


st.code("""st.map(filtered_data)
""", language='python')  

DATE_COLUMN = 'date'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
            'streamlit-demo-data/uber-raw-data-sep14.csv.gz')


#@st.cache
#def load_data(nrows):
#    data = pd.read_csv(DATA_URL, nrows=nrows)
#    lowercase = lambda x: str(x).lower()
#    data.rename(lowercase, axis='columns', inplace=True)
#    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
#    return data
@st.cache
def load_data(nrows):
    data = pd.read_csv('/app/src/time_series_covid19_confirmed_global.csv')
    data = data.rename(columns={"Province/State": "province", "Country/Region": "conuntry","Lat":"lat","Long":"lon"})
    data = data.melt(id_vars=["province", "conuntry","lat","lon"], 
        var_name="date", 
        value_name="value")
    data['date'] = pd.to_datetime(data['date'],format='%m/%d/%y')
    return data

data_load_state = st.text('Loading data...')
data = load_data(10000)
data_load_state.text('Loading data... done!')


# Filters UI
subset_data = data
country_name_input = st.sidebar.multiselect(
'Country name',
data.groupby('conuntry').count().reset_index()['conuntry'].tolist())
# by country name
if len(country_name_input) > 0:
    subset_data = data[data['conuntry'].isin(country_name_input)]

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

st.subheader('Number of pickups by hour')
hist_values = np.histogram(data[DATE_COLUMN], bins=24, range=(0,24))[0]
st.bar_chart(hist_values)
st.bar_chart(data)
# Some number in the range 0-23
hour_to_filter = st.slider('hour', 0, 23, 17)
filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

st.subheader('Map of all pickups at %s:00' % hour_to_filter)
st.map(filtered_data)
