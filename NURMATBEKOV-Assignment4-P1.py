import pandas as pd
import altair as alt
import streamlit as st

# reading only necessary columns 
data = pd.read_csv('data/total.csv',
                   header=0,
                   usecols=['COU', 'Country', 'POL',
                             'Pollutant', 'VAR', 'Variable',
                             'Year','Unit Code', 'Unit',
                             'PowerCode Code', 'PowerCode','Value'])

chart_data = data.loc[((data.Year == 1990) | (data.Year == 2010)) & 
                    (data['Unit Code'] == 'T_CO2_EQVT') &
                    (data.PowerCode == 'Thousands')]

# altair doesn't allow to use custom str values for group bar charts
descriptions = ['Energy', 'Manufacturing',
             'Transport', 'Residential', 'Other']
fields = ['ENER_IND', 'ENER_MANUF', 'ENER_TRANS', 'ENER_OSECT', 'ENER_OTH']
for i in range(len(descriptions)):
    chart_data.replace(fields[i], descriptions[i], inplace=True, regex=True)

chart = alt.Chart(chart_data, title="Greenhouse gas emissions by sector in 1990 and 2010").mark_bar(
).transform_filter(
    alt.FieldOneOfPredicate(field='VAR',
                            oneOf=descriptions)
).transform_calculate(
    mill_value = 'datum.Value/1000',
).encode(
    alt.Y('mill_value:Q',
          axis=alt.Axis(
              tickCount=5,
              domainWidth=0,
              title='CO2 equivalent (megatonnes)',
              titleFontWeight='lighter',              
              titlePadding=10
          )
         ),
    alt.Color('Year:O',
              legend=alt.Legend(title='Years',
                                titleFontSize=12,
                                labelFontSize=12,
                                titlePadding=10,
                                titleFontWeight='lighter'
                               )
             ),
    alt.X('Year:O', axis=None),
    alt.Column('VAR:N',
               title=None,
               sort=alt.EncodingSortField(
                   op='max',
                   field='mill_value',
                   order='descending'),
               header=alt.Header(
                   orient='bottom',
                   labelAnchor='end',
                   labelAngle=-50,
                   labelBaseline='line-bottom',
                   labelLineHeight=30,
                   labelPadding=15,
                   labelFontSize=10
               )
              )
).configure_view(
    strokeWidth=0
).configure_title(
    fontWeight='normal',
    dy=-10,
    dx=40
)

st.write(chart)