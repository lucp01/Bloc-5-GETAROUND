import streamlit as st
import pandas as pd
import plotly.express as px 
import numpy as np
import plotly.io as pio
import plotly.graph_objects as go
import plotly.offline as pyo
import plotly.offline as py
import plotly.tools as tls
from plotly.subplots import make_subplots
import io
pd.options.mode.chained_assignment = None

st.set_page_config(page_title='Getaround - Luc Parat',layout='wide')
st.markdown("Project Getaround - Luc Parat 2024")
st.title("GetAround Dashboard")
st.markdown("""GetAround is the Airbnb for cars. Founded in 2009, this company has known rapid growth. In 2019, they count over 5 million users and about 20K available cars worldwide.
When using Getaround, drivers book cars for a specific time period, from an hour to a few days long. They are supposed to bring back the car on time, but it happens from time to time that drivers are late for the checkout.

Late returns at checkout can generate high friction for the next driver if the car was supposed to be rented again on the same day : Customer service often reports users unsatisfied because they had to wait for the car to come back from the previous rental or users that even had to cancel their rental because the car wasn’t returned on time.             

In order to mitigate those issues we’ve decided to implement a minimum delay between two rentals. A car won’t be displayed in the search results if the requested checkin or checkout times are too close from an already booked rental.

It solves the late checkout issue but also potentially hurts Getaround/owners revenues: we need to find the right trade off.""")

st.markdown('***') #################

#@st.cache(allow_output_mutation=True)
def load_pricing():
  pricing =  pd.read_csv('https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_pricing_project.csv')
  return pricing

#@st.cache(allow_output_mutation=True)
def load_data_original():
  data_original = pd.read_excel('https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_delay_analysis.xlsx')
  return data_original

#@st.cache(allow_output_mutation=True)
def load_documentation():
  documentation = pd.read_excel('https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_delay_analysis.xlsx', 'Documentation')
  return documentation

#@st.cache(allow_output_mutation=True)
def load_data():
  data = pd.read_excel('https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_delay_analysis.xlsx')
  return data

pricing = load_pricing()
data_original = load_data_original()
documentation = load_documentation()
data = load_data()

# add new columns
data['delay_checkout_status'] = data['delay_at_checkout_in_minutes'].fillna('blank')
data.loc[data['delay_at_checkout_in_minutes']<=0 ,['delay_checkout_status']]='ontime'
data.loc[data['delay_at_checkout_in_minutes']>0 ,['delay_checkout_status']]='delay'

data["delay_checkout_status_2"] = data["state"] + " - " + data["delay_checkout_status"]

data['time_delta_status'] = data['time_delta_with_previous_rental_in_minutes'].fillna('blank')
data.loc[data['time_delta_with_previous_rental_in_minutes']<=0 ,['time_delta_status']]='ontime'
data.loc[data['time_delta_with_previous_rental_in_minutes']>0 ,['time_delta_status']]='delay'

data["time_delta_status_2"] = data["state"] + " - " + data["time_delta_status"]
data.loc[data['time_delta_status_2'] == "ended - blank",['time_delta_status_2']]='Single'
data.loc[data['time_delta_status_2'] == "canceled - blank",['time_delta_status_2']]='Single'
data.loc[data['time_delta_status_2'] == "ended - delay",['time_delta_status_2']]='Previous - ended - delay'
data.loc[data['time_delta_status_2'] == "ended - ontime",['time_delta_status_2']]='Previous - ended - ontime'
data.loc[data['time_delta_status_2'] == "canceled - delay",['time_delta_status_2']]='Previous - canceled - delay'
data.loc[data['time_delta_status_2'] == "canceled - ontime",['time_delta_status_2']]='Previous - canceled - ontime'

data["time_delta_status_3"] = data["state"] + " - " + data["time_delta_status"]
data.loc[data['time_delta_status_3'] == "ended - blank",['time_delta_status_3']]='ended'
data.loc[data['time_delta_status_3'] == "ended - delay",['time_delta_status_3']]='ended'
data.loc[data['time_delta_status_3'] == "ended - ontime",['time_delta_status_3']]='ended'

data["time_delta_status_4"] = data["time_delta_status"]
data.loc[data['time_delta_status_4'] == "blank",['time_delta_status_4']]='Single rental'
data.loc[data['time_delta_status_4'] == "delay",['time_delta_status_4']]='Multiple (previous) rental'
data.loc[data['time_delta_status_4'] == "ontime",['time_delta_status_4']]='Multiple (previous) rental'

data["ontime_delay_status"] = data["time_delta_status_4"] + " - " + data["delay_checkout_status"]

# add checkbox
if st.checkbox('Princing dataset'): st.write(pricing)
if st.checkbox('Data original'): st.write(data_original)
if st.checkbox('Documentation'): st.write(documentation)
if st.checkbox('Data'): st.write(data)

st.markdown('***') #################

col1, col2, col3, = st.columns(3)
with col1:
    st.subheader('Main statistics')

    average_rental_price_per_day = round(pricing['rental_price_per_day'].mean())
    st.write (f'The average car rental price per day is {average_rental_price_per_day} Euros.')

    number_of_cars = len(data['car_id'].unique())
    st.write (f'There are {number_of_cars} differents cars.')

    number_of_rentals = data.shape[0]
    st.write (f'There are {number_of_rentals} rentals in the dataset.')

    number_of_consecutive_rentals = (data['time_delta_with_previous_rental_in_minutes']).count()
    proportion_of_consecutive_rentals = (number_of_consecutive_rentals / number_of_rentals)
    st.write (f'There are {number_of_consecutive_rentals} consecutives rentals, who represents {round(proportion_of_consecutive_rentals,2)*100}% of the full dataset.')

    average_delay_checkout = round(data['delay_at_checkout_in_minutes'].mean())
    st.write (f'The average delay at checkout is {average_delay_checkout} minutes.')
 
    average_time_delta_with_previous = round(data['time_delta_with_previous_rental_in_minutes'].mean())
    st.write (f'The average time delta with previous rental is {average_time_delta_with_previous} minutes.')

with col2:
    st.subheader('')
with col3:
    st.subheader('')

st.markdown('***') #################

st.subheader('Data analysis')
st.markdown('All rentals')
describe = data.describe(include='all').round().astype(str).apply(lambda x: x.replace('.0',''))
st.write (describe)

st.markdown('***') #################

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader('Two Interfaces: Mobile or Connect')
    fig = px.pie(data, names='checkin_type', title='')
    st.plotly_chart(fig , use_container_width=True)
with col2:
    st.subheader('Interfaces by Rental States')
    fig = px.histogram(data, 
            x ='checkin_type',
            color = 'state',
            barmode ='group',
            width= 600,
            height = 500,
            histnorm = 'percent',
            text_auto = True)
    fig.update_traces(textposition = 'outside', textfont_size = 15, texttemplate='%{y:.0f}')
    fig.update_layout(margin=dict(l=50,r=50,b=50,t=50,pad=4),
            yaxis = {'visible': False}, 
            xaxis = {'visible': True})
    fig.update_xaxes(tickfont_size=15)                     
    st.plotly_chart(fig)
with col3:
    st.subheader('Interfaces by Checkout Status')
    fig = px.histogram(data,
            x='checkin_type',
            color='delay_checkout_status',
            barmode = 'group',
            width = 600,
            height = 500,
            histnorm = 'percent',
            text_auto = True)
    fig.update_traces(textposition = 'outside', textfont_size = 15,texttemplate='%{y:.0f}')
    fig.update_layout(margin=dict(l=50,r=50,b=50,t=50,pad=4),
            yaxis = {'visible': False}, 
            xaxis = {'visible': True})
    fig.update_xaxes(tickfont_size=15)                     
    st.plotly_chart(fig)

st.markdown('***') #################

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader('Two States: Ended or Canceled')
    fig = px.pie(data, names='state', title='')
    st.plotly_chart(fig , use_container_width=True)
with col2:
    st.subheader('Three Checkout Possibilities: Ontime, Delay or Not Filled (blank)')
    fig = px.pie(data, names='delay_checkout_status', title='')
    st.plotly_chart(fig , use_container_width=True)
with col3:
    st.subheader('')

st.markdown('***') #################

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader('Two rental types: Single or Multiple (previous)')
    fig = px.pie(data, names='time_delta_status_4', title='')
    st.plotly_chart(fig , use_container_width=True)
with col2:
    st.subheader('Single/Multiple per Ontine/Delay')
    fig = px.pie(data, names='ontime_delay_status', title='')
    st.plotly_chart(fig , use_container_width=True)
with col3:
    st.subheader('')

st.markdown('***') #################

st.subheader(f'Exploration of the {number_of_rentals} checkout (single & multiple rental)')

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('**Checkout Categories**')
    fig = px.pie(data, names='delay_checkout_status_2', title='')
    st.plotly_chart(fig , use_container_width=True)
with col2:
    option = ['delay']
    delta = data.loc[data['delay_checkout_status'].isin(option)]
    delay_rental = delta['delay_checkout_status'].count()
    st.markdown(f'**Checkout Delay - Distribution of the {delay_rental} cases**')
    fig = px.histogram(delta[(delta['delay_at_checkout_in_minutes']<(2*delta['delay_at_checkout_in_minutes'].std()))]['delay_at_checkout_in_minutes'], x='delay_at_checkout_in_minutes')
#   .std() -> return the standard deviation of the elements.
    st.plotly_chart(fig, use_container_width=True)
with col3:
    option = ['ontime']
    delta=data.loc[data['delay_checkout_status'].isin(option)]
    ontime_rental = delta['delay_checkout_status'].count()
    st.markdown(f'**Checkout Ontime - Distribution of the {ontime_rental} case**')
    fig = px.histogram(delta[(delta['delay_at_checkout_in_minutes']<(2*delta['delay_at_checkout_in_minutes'].std()))]['delay_at_checkout_in_minutes'], x='delay_at_checkout_in_minutes')
#   .std() -> return the standard deviation of the elements.
    st.plotly_chart(fig, use_container_width=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('')
with col2:
    with st.form('Checkout delay'):
        start_range = st.number_input("Starting range per slices of 60 minutes - Select", min_value=0, step=60)
        end_range = st.number_input("Ending range per slices of 60 minutes - Select", min_value=0, step=60)
        submit = st.form_submit_button('submit')
        if submit:
            delta = data.where(data['delay_checkout_status'] == 'delay')
            mask = (delta['delay_at_checkout_in_minutes']<=end_range) & (delta['delay_at_checkout_in_minutes']>=start_range)
            filter = delta[mask]
            rental = filter['delay_at_checkout_in_minutes'].count()
            rental_perc = (rental / delta.shape[0]) * 100
            st.metric('Number of concerning rentals', rental)
            st.markdown(f'These {rental} delayed checkout represents {round(rental_perc,2)}% of the full dataset composed of 21310 cases.')
with col3:
    with st.form('Checkout ontime'):
        start_range = st.number_input("Starting range per slices of 60 minutes - Select", min_value=-9000, step=-60)
        end_range = st.number_input("Ending range per slices of 60 minutes - Select", min_value=0, step=-60)
        submit = st.form_submit_button('submit')
        if submit:
            delta = data.where(data['delay_checkout_status'] == 'ontime')
            mask = (delta['delay_at_checkout_in_minutes']<=end_range) & (delta['delay_at_checkout_in_minutes']>=start_range)
            filter = delta[mask]
            rental = filter['delay_at_checkout_in_minutes'].count()
            rental_perc = (rental / delta.shape[0]) * 100
            st.metric('Number of concerning rentals', rental)
            st.markdown(f'These {rental} ontime checkout represents {round(rental_perc,2)}% of the full dataset composed of 21310 cases.')

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.markdown('')
with col2:
    st.markdown('Checkout - Blank')
    describe1 = data.where(data['delay_checkout_status'] == 'blank')
    describe1 = describe1['delay_checkout_status'].describe(include='all').round().astype(str).apply(lambda x: x.replace('.0',''))
    st.write (describe1)
with col3:
    st.markdown('Checkout - Delay')
    describe2 = data.where(data['delay_checkout_status'] == 'delay')
    describe2 = describe2['delay_checkout_status'].describe(include='all').round().astype(str).apply(lambda x: x.replace('.0',''))
    st.write (describe2)
with col4:
    st.markdown('')
with col5:
    st.markdown('Checkout - Ontime')
    describe3 = data.where(data['delay_checkout_status'] == 'ontime')
    describe3 = describe3['delay_checkout_status'].describe(include='all').round().astype(str).apply(lambda x: x.replace('.0',''))
    st.write (describe3)
with col6:
    st.markdown('')

st.markdown('***') #################

st.subheader(f'Exploration of the {number_of_consecutive_rentals} time delta for consecutives rentals, representing {round(proportion_of_consecutive_rentals,2)*100}% of the full dataset.')
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('**Previous-Multiple rentals splitted by categories**')
    fig = px.pie(data, names='time_delta_status_2', title='')
    st.plotly_chart(fig , use_container_width=True)
with col2:
    option = ['ended']
    delta = data.loc[data['state'].isin(option)]
    ended_previous_rental = delta['time_delta_with_previous_rental_in_minutes'].count()
    st.markdown(f'**Ended (Delay & Ontime) - Distribution of the {ended_previous_rental} cases**')
    fig = px.histogram(delta['time_delta_with_previous_rental_in_minutes'],x='time_delta_with_previous_rental_in_minutes')
    st.plotly_chart(fig, use_container_width=True)
with col3:
    option = ['canceled']
    delta = data.loc[data['state'].isin(option)]
    canceled_previous_rental = delta['time_delta_with_previous_rental_in_minutes'].count()
    st.markdown(f'**Cancelled (Delay & Ontime) - Distribution of the {canceled_previous_rental} cases**')
    fig = px.histogram(delta['time_delta_with_previous_rental_in_minutes'],x='time_delta_with_previous_rental_in_minutes')
    st.plotly_chart(fig, use_container_width=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('')
with col2:
    with st.form('Multiple rental - Ended'):
        start_range = st.number_input("Starting range per slices of 30 minutes - Select", min_value=0, step=30)
        end_range = st.number_input("Ending range per slices of 30 minutes - Select", min_value=0, step=30)
        submit = st.form_submit_button('submit')
        if submit:
            delta = data.where(data['state'] == 'ended')
            mask = (delta['time_delta_with_previous_rental_in_minutes']<=end_range) & (delta['time_delta_with_previous_rental_in_minutes']>=start_range)
            filter = delta[mask]
            rental = filter['time_delta_with_previous_rental_in_minutes'].count()
            category = (data['time_delta_with_previous_rental_in_minutes']).count()
            rental_perc = (rental / category) * 100
            st.metric('Number of concerning rentals', rental)
            st.markdown(f'These {rental} ended rentals represents {round(rental_perc,2)}% of the {category} multiple rental.')
with col3:
    with st.form('Multiple rental - Canceled'):
        start_range = st.number_input("Starting range per slices of 30 minutes - Select", min_value=0, step=30)
        end_range = st.number_input("Ending range per slices of 30 minutes - Select", min_value=0, step=30)
        submit = st.form_submit_button('submit')
        if submit:
            delta = data.where(data['state'] == 'canceled')
            mask = (delta['time_delta_with_previous_rental_in_minutes']<=end_range) & (delta['time_delta_with_previous_rental_in_minutes']>=start_range)
            filter = delta[mask]
            rental = filter['time_delta_with_previous_rental_in_minutes'].count()
            category = (data['time_delta_with_previous_rental_in_minutes']).count()
            rental_perc = (rental / category) * 100
            st.metric('Number of concerning rentals', rental)
            st.markdown(f'These {rental} cancelled rentals represents {round(rental_perc,2)}% of the {category} multiple rental.')

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.markdown('')
with col2:
    st.markdown('Single')
    describe4 = data.where(data['time_delta_status_2'] == 'Single')
    describe4 = describe4['time_delta_status_2'].describe(include='all').round().astype(str).apply(lambda x: x.replace('.0',''))
    st.write (describe4)
with col3:
    st.markdown('Ended - Delay')
    describe5 = data.where(data['time_delta_status_2'] == 'Previous - ended - delay')
    describe5 = describe5['time_delta_status_2'].describe(include='all').round().astype(str).apply(lambda x: x.replace('.0',''))
    st.write (describe5)
with col4:
    st.markdown('Ended - Ontime')
    describe6 = data.where(data['time_delta_status_2'] == 'Previous - ended - ontime')
    describe6 = describe6['time_delta_status_2'].describe(include='all').round().astype(str).apply(lambda x: x.replace('.0',''))
    st.write (describe6)
with col5:
    st.markdown('Cancel - Delay')
    describe7 = data.where(data['time_delta_status_2'] == 'Previous - canceled - delay')
    describe7 = describe7['time_delta_status_2'].describe(include='all').round().astype(str).apply(lambda x: x.replace('.0',''))
    st.write (describe7)
with col6:
    st.markdown('Cancel - Ontime')
    describe8 = data.where(data['time_delta_status_2'] == 'Previous - canceled - ontime')
    describe8 = describe8['time_delta_status_2'].describe(include='all').round().astype(str).apply(lambda x: x.replace('.0',''))
    st.write (describe8)

st.markdown('***') #################
st.subheader('Goals 🎯 and --> Conclusions')
st.markdown ("""
**Our Product Manager still needs to decide:**
* **threshold:** how long should the minimum delay be? **--> 60 minutes (average delay at checkout)**
* **scope:** should we enable the feature for all cars?, only Connect cars? **--> Connect car represents only 20% of entire flow, so we can probably enable Mobile device for all cars if technically possible** 

In order to help them make the right decision, they are asking you for some data insights. Here are the first analyses they could think of, to kickstart the discussion. Don’t hesitate to perform additional analysis that you find relevant.

* Which share of our owner’s revenue would potentially be affected by the feature? **---> The flow's split is 80% Mobile vs 20% Connect.**
* How many rentals would be affected by the feature depending on the threshold and scope we choose? **---> 9404 cases had delays at checkout vs 6942 ontime. 5018 rental had 60 minutes delays (23% of the entire rentals). So if we choose 60 minutes delay the 4400 others cases with more than 60 minutes delay would be affected.**
* How often are drivers late for the next check-in? **---> 85% (1368 + 194 = 1562 drivers late for next checkin from 1841 consecutive rentals).**
* How does it impact the next driver? **---> Impact is 9% cancellation. 194 cancellations of the 1841 consecutive rentals due to delay.**
* How many problematic cases will it solve depending on the chosen threshold and scope? **---> 194 cancellations due to delays between 30 & 720 minutes. 30 to 120 minutes threshold could avoid 52 of the 194 cancellations.**
""")

st.markdown('***') #################

st.markdown ("""
By Luc Parat 😎 2024/07

lucparat1@gmail.com

https://share.vidyard.com/
""")