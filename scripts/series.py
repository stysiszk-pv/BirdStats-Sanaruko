import streamlit as st
import pandas as pd

# read csv file
df = pd.read_csv('data/testdata.csv')

# convert date to datetime
df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

st.title('佐鳴湖における鳥類個体数の推移')
st.subheader('浜松野鳥の会')
st.text('This page was made by S.I., 2025/08/15.')
# select species
species = df.columns[1:]
selected_species = st.multiselect('表示する種を選択してください', species, default=list())

# display selected species data
if selected_species:
    st.line_chart(df.set_index('date')[selected_species])
else:
    st.info('表示する種を選択してください')

# show datatable
with st.expander('データテーブルを表示'):
    st.dataframe(df)