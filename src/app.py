import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import datetime

st.title('Covid19 Dashboard')

st.markdown('The dashboard will visualize the Covid-19 Situation in the World')
st.markdown('Coronavirus disease (COVID-19) is an infectious disease caused by a newly discovered coronavirus. Most people infected with the COVID-19 virus will experience mild to moderate respiratory illness and recover without requiring special treatment.')

st.sidebar.title("Visualization Selector")
st.sidebar.markdown("Select the Charts/Plots accordingly:")


#st.code("""st.map(filtered_data)
#""", language='python')  

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
CASES_COLUMN = 'cases'
baseFolder = '/app/src/'

def read_data(name):
  df = pd.read_csv(baseFolder+name)
  df = df.rename(columns={"Province/State": "province", "Country/Region": "country","Lat":"lat","Long":"lon"})
  return df

def meltData(df):
  df = df.melt(id_vars=["province", "country","lat","lon"], 
        var_name="date", 
        value_name="cases")
  return df

@st.cache
def load_data():
  data = pd.DataFrame()
  files = ['time_series_covid19_confirmed_global.csv','time_series_covid19_recovered_global.csv','time_series_covid19_deaths_global.csv']
  for file in files :
    df2 = read_data(file)
    df2 = meltData(df2)
    df2[DATE_COLUMN] = pd.to_datetime(df2[DATE_COLUMN],format='%m/%d/%y')
    if file == 'time_series_covid19_confirmed_global.csv':
      df2["type"] = 'c'
    elif file == 'time_series_covid19_recovered_global.csv' :
      df2["type"] = 'r'
    elif file == 'time_series_covid19_deaths_global.csv':
      df2["type"] = 'd'
    data = data.append(df2)
  return data
    
#@st.cache
#def load_data(nrows):
#    data = pd.read_csv('/app/src/time_series_covid19_confirmed_global.csv')
#    data = data.rename(columns={"Province/State": "province", "Country/Region": "conuntry","Lat":"lat","Long":"lon"})
#    data = data.melt(id_vars=["province", "conuntry","lat","lon"], 
#        var_name="date", 
#        value_name="value")
#    data['date'] = pd.to_datetime(data['date'],format='%m/%d/%y')
#    return data

data_load_state = st.text('Loading data...')
data = load_data()
data_load_state.text('Loading data... done!')

### data today metrincs
maxDate = data['date'].max()
yesterday = maxDate - datetime.timedelta(days=1)
maxdate = np.datetime64(maxDate)
dt64 = np.datetime64(yesterday)
print(maxdate,"y ", dt64)
pdate = maxDate.strftime("%m/%d/%Y")

filtered_data = data.loc[(data[DATE_COLUMN] == dt64)]
toDay_data = data.loc[(data[DATE_COLUMN] == maxdate)]

df1 = toDay_data.groupby(['type'])[CASES_COLUMN].sum().sort_values(ascending=False).iloc[:5]
df2 = filtered_data.groupby(['type'])[CASES_COLUMN].sum().sort_values(ascending=False).iloc[:5]

newCases = df1 - df2 

print('**Total new cases:** {}  \n'.format(newCases['c']))
print('**Total new Deaths:** {}  \n'.format(newCases['d']))
print('**Total new Recoverd:** {}  \n'.format(newCases['r']))


st.subheader('Informacion Global fecha {} '.format(pdate))
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Confirmed")
    st.metric("", '{:,}  \n'.format(df1['c']), '{:,} '.format(newCases['c']))

with col2:
    st.subheader("Deaths")
    st.metric("", '{:,}  \n'.format(df1['d']), '{:,} '.format(newCases['d']))

with col3:
    st.subheader("Recoverd")
    st.metric("", '{:,}  \n'.format(df1['r']), '{:,} '.format(newCases['r']))


## global comportamiento
global_by_date = data.groupby(['date','type'])[CASES_COLUMN].sum().sort_values().to_frame().reset_index()
global_by_date = global_by_date.set_index('date')
global_by_month2 = global_by_date.groupby([pd.Grouper(freq='M'),'type']).max().reset_index()

globalByMonth_graph = alt.Chart(global_by_month2).transform_filter(
    alt.datum.cases > 0  
).mark_line().encode(
    x=alt.X('date:T', type='temporal', title='Date'),
    y=alt.Y('cases',  title='Number cases'),
    tooltip = 'cases',
    color='type'
).properties(
).configure_axis(
    labelFontSize=17,
    titleFontSize=20
)

with st.container():
  st.subheader("Comportamiento :")
  st.altair_chart(globalByMonth_graph,use_container_width=True)

    
col1g, col2g = st.columns(2)
### Top5 countries confirmed

grouped_data = toDay_data.groupby(['country','type'])[CASES_COLUMN].sum().sort_values(ascending=False)
top5 = grouped_data.to_frame().reset_index()
top5Countries = top5.iloc[:5,0]
print(top5Countries)
top5 = top5.loc[top5['country'].isin(top5Countries.values)]
top5 = top5.sort_values(by='cases', ascending=False)

top5_graph = alt.Chart(top5).mark_bar().encode(
    x=alt.X('type'),
    y=alt.Y('cases', sort=None),
    color='type',
    column='country'
).properties(
  width=100,
    height=300
).configure_axisX(
    titleAngle=0,
    labelAngle=0
)

st.altair_chart(top5_graph)

# Filters UI

st.sidebar.metric(label="Fecha", value=pdate, delta="")

subset_data = data
country_name_input = st.sidebar.multiselect(
'Country name',
data.groupby('country').count().reset_index()['country'].tolist())
# by country name
if len(country_name_input) > 0:
    subset_data = data[data['country'].isin(country_name_input)]

maxDate = data['date'].max()
maxdate = np.datetime64(maxDate)
filtered_data = data[data[DATE_COLUMN] == maxdate]
#filtered_data = filtered_data.loc[:, ['lat','lon']]
filtered_data['lat'] = filtered_data['lat'].apply(lambda x: pd.to_numeric(x))
filtered_data['lon'] = filtered_data['lon'].apply(lambda x: pd.to_numeric(x))
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(global_by_month2)
    st.write(filtered_data)

st.subheader('Number of pickups by hour')
#hist_values = np.histogram(data[DATE_COLUMN], bins=24, range=(0,24))[0]
#st.bar_chart(hist_values)
#st.bar_chart(data)
# Some number in the range 0-23
hour_to_filter = st.slider('hour', 0, 23, 17)
#filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

st.subheader('Map of all pickups at %s:00' % hour_to_filter)
st.map(filtered_data)
