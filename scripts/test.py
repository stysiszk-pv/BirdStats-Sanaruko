# This is a test file to demonstrate Streamlit functionality
# This file is not used to make BirdStats_Sanaruko

import streamlit as st
import openpyxl
import pandas as pd

# read excel file
df = pd.read_excel('data/Bird_Sanaruko.xlsx', sheet_name = 'obs_df')
##SpeciesID as column names
df_spID = pd.read_excel('data/Bird_Sanaruko.xlsx', sheet_name = 'ObsTable')
##Taxonomy table
df_tax = pd.read_excel('data/Bird_Sanaruko.xlsx', sheet_name = 'TaxTable')
##Weather table
df_weath = pd.read_excel('data/Bird_Sanaruko.xlsx', sheet_name = 'weather')

# convert date to datetime
df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
df_spID['date'] = pd.to_datetime(df_spID['date'], format='%Y%m%d')
df_weath['date'] = pd.to_datetime(df_weath['date'], format='%Y%m%d')

# calculate the maximum number of birds of each species for each year
df_max = df.groupby(df['date'].dt.year).max()

# add year
df_yr = df.copy()
df_yr['year'] = df_yr['date'].dt.year

# list to store results
results = []

# process for each species
species_list = df_yr.columns[1:-1]  # columns other than 'date' and 'year'
for species in species_list:
    for year, group in df_yr.groupby('year'):
        max_count = group[species].max()
        max_date = group[group[species] == max_count]['date'].iloc[0] if max_count > 0 else None
        results.append({
            'species': species,
            'year': year,
            'max_count': max_count,
            'max_date': max_date
        })

# convert the result list to a dataframe 
result_df = pd.DataFrame(results)
# add month
result_df['month'] = result_df.max_date.dt.month if result_df['max_date'].notnull().any() else None
# sort by species and year
result_df = result_df.sort_values(by=['species', 'year'])

# convert max_date to string (empty if None)
#result_df['max_date'] = result_df['max_date'].dt.strftime('%Y-%m-%d')

st.dataframe(species_list)

# select species
species = df_max.columns[1:]
selected_species = st.multiselect('表示する種を選択してください', species, default=list())

tab1, tab2, tab3 = st.tabs(["種ごとの推移", "最大個体数を観測した月", "Histgram"])

#show df_max
with tab1: 
    with tab1: 
        if selected_species: 
            st.line_chart(df.set_index('date')[selected_species])
        else: 
            st.info('表示する種を選択してください')

with tab2: 
    if selected_species: 
        st.dataframe(result_df.loc[result_df['species'].isin(selected_species)])
    else:
        st.info('表示する種を選択してください')

with tab3: 
    if selected_species: 
        result_df_selc = result_df.loc[result_df['species'].isin(selected_species), ['species', "month"]]
        result_df_selc = result_df_selc.groupby(['species', 'month']).size().reset_index(name='count')
        st.dataframe(result_df_selc)
    else:
        st.info('表示する種を選択してください')