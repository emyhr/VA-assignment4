import pandas as pd
import altair as alt
import streamlit as st
import json
import geopandas as gpd


# reading only necessary columns
data = pd.read_csv('data/total.csv',
                   header=0,
                   usecols=['COU', 'Country', 'POL',
                             'Pollutant', 'VAR', 'Variable',
                             'Year','Unit Code', 'Unit',
                             'PowerCode Code', 'PowerCode','Value'])
# geo-file
file = open('data/custom.geo.json')
geo_data = json.load(file)
gdf = gpd.GeoDataFrame.from_features(geo_data)
gdf.rename(columns={'iso_a3': 'COU'}, inplace=True)
gdf = gdf.loc[:, ['geometry', 'COU', 'continent']]
gdf = gdf.loc[gdf.continent == 'Europe']

# dropping columns unnecessary for analysis
extra_columns = ['Country', 'Pollutant',
                 'Variable', 'Unit', 'PowerCode Code']
data.drop(extra_columns, axis=1, inplace=True)

# data for charts
data1990 = data.loc[(data.Year == 1990) &
                    (data.POL == 'CO2') &
                    (data['Unit Code'] == 'T_CO2_EQVT') &
                    (data.PowerCode == 'Thousands') &
                    (data.VAR == 'TOTAL')]
gdf_1990 = gdf.merge(data1990, on='COU', how='left')

data2010 = data.loc[(data.Year == 2010) &
                    (data.POL == 'CO2') &
                    (data['Unit Code'] == 'T_CO2_EQVT') &
                    (data.PowerCode == 'Thousands') &
                    (data.VAR == 'TOTAL')]
gdf_2010 = gdf.merge(data2010, on='COU', how='left')

# adding a couple more columns for labels
gdf_2010['centroid_lon'] = gdf_2010['geometry'].centroid.x
gdf_2010['centroid_lat'] = gdf_2010['geometry'].centroid.y
gdf_1990['centroid_lon'] = gdf_1990['geometry'].centroid.x
gdf_1990['centroid_lat'] = gdf_1990['geometry'].centroid.y

# converting to json reading back (needed for geo data)
choro_1990_json = json.loads(gdf_1990.to_json())
choro_1990_data = alt.Data(values=choro_1990_json['features'])
choro_2010_json = json.loads(gdf_2010.to_json())
choro_2010_data = alt.Data(values=choro_2010_json['features'])

# -------------------- Choropleth map 1990 ----------------------------#
# Add Base Layer
base_1990 = alt.Chart(choro_1990_data, title = 'Total CO2 emissions in 1990').mark_geoshape(
    stroke='black',
    strokeWidth=0.4,
    fill = 'lightgray'
).encode(
).properties(
    width=300,
    height=300
)
# Add Choropleth Layer
choro_1990 = alt.Chart(choro_1990_data).mark_geoshape(
    stroke='black'
).encode(
    color = alt.Color('properties.Value',
                      type='quantitative',
                      scale=alt.Scale(scheme='goldorange'),
                      legend=alt.Legend(
                          labelColor='grey',
                          labelLimit=30,
                          labelFontSize=7),
                      title="Thousands of tonnes"),

    tooltip = alt.Tooltip(['properties.Value:Q', 'properties.COU:N'])

)

# Add Labels Layer
labels_1990 = alt.Chart(choro_1990_data).mark_text(baseline='top'
 ).properties(
    width=400,
    height=400
 ).encode(
     longitude='properties.centroid_lon:Q',
     latitude='properties.centroid_lat:Q',
     text='properties.COU:N',
     size=alt.value(10)
 )

chart_1990 = base_1990 + choro_1990 + labels_1990

# -------------------- Choropleth map 1990 ----------------------------#
# Add Base Layer
base_2010 = alt.Chart(choro_2010_data, title = 'Total CO2 emissions in 2010').mark_geoshape(
    stroke='black',
    strokeWidth=0.4,
    fill = 'lightgray'
).encode(
).properties(
    width=300,
    height=300
)
# Add Choropleth Layer
choro_2010 = alt.Chart(choro_2010_data).mark_geoshape(
    stroke='black'
).encode(
    color = alt.Color('properties.Value',
                      type='quantitative',
                      scale=alt.Scale(scheme='goldorange',
                                      domain=[2*10**4, 10**8]
                                     ),
                      legend=alt.Legend(
                          labelColor='grey',
                          labelLimit=30,
                          labelFontSize=7),
                      title="Thousands of tonnes"),

    tooltip = alt.Tooltip(['properties.Value:Q', 'properties.COU:N'])

)

# Add Labels Layer
labels_2010 = alt.Chart(choro_1990_data).mark_text(baseline='top'
 ).properties(
    width=400,
    height=400
 ).encode(
     longitude='properties.centroid_lon:Q',
     latitude='properties.centroid_lat:Q',
     text='properties.COU:N',
     size=alt.value(10)
 )

chart_2010 = base_2010 + choro_2010 + labels_2010

final_chart = alt.concat(chart_1990, chart_2010).resolve_scale(color='independent')
st.write(final_chart)