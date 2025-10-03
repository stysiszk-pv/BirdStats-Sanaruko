import streamlit as st
import openpyxl
import pandas as pd
import numpy as np
import sys
import os

# モジュールの検索パスにスクリプトのディレクトリを追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts import bg_cancelled as bg

st.set_page_config(page_title="種別個体数", page_icon="📊")

# read excel file
df = pd.read_excel('data/Bird_Sanaruko.xlsx', sheet_name = 'obs_df')
df_tax = pd.read_excel('data/Bird_Sanaruko.xlsx', sheet_name = 'TaxTable')
df_weath = pd.read_excel('data/Bird_Sanaruko.xlsx', sheet_name = 'weather')

# convert date to datetime
df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
df_weath['date'] = pd.to_datetime(df_weath['date'], format='%Y%m%d')

# merge weather and observation data
df_display = df_weath.merge(df, on='date', how='left')

# set page titles
st.title('種別個体数の推移')
st.write('#####  浜松野鳥の会')

# Abstract of this page
st.write('###')
with st.expander('このページの使い方', expanded=True):
    st.markdown('''
                1. 集計期間を設定  
                渡り鳥 (特に冬鳥) の滞在期間は暦上の年をまたぐ場合があります.  
                従って, 種ごとの滞在期間に合わせて最大個体数の集計期間を設定する必要があります.  
                "集計期間を設定"のセクションを展開し, 集計期間の開始月を設定してください.  
                デフォルトは5月-翌4月です。
                
                2. 種を選択  
                リストから個体数を確認したい種を選択してください (複数選択可).  
                最初のタブで種ごとの個体数の年次推移を確認できます.  
                2番目のタブでは各年の最大個体数を確認できます.  
                3番目のタブでは各年の最大個体数を観測した月を確認できます.  
                4番目のタブでは種ごとの月別個体数を確認できます.  
                ''')
st.write('#')

# set the biological year
with st.expander('集計期間を設定'): 
    blyr_st = st.selectbox("集計期間の始まりの月を選択してください.", 
                       options = np.arange(1, 13), 
                       index = 4,  # default to May
                       placeholder='月を選択してください.', 
                       )
    st.write(blyr_st, '月から1年間を集計期間とします.')

# add biological year column
# months earlier than the 1st month of the biological year are considered to be those in the last biological year
df_blyr = df.copy()
df_blyr['biological_year'] = np.where(df_blyr['date'].dt.month >= blyr_st, 
                                      df_blyr['date'].dt.year, 
                                      df_blyr['date'].dt.year - 1, 
                                      )

# calculate the maximum number of birds of each species for each year
df_max = df.groupby(df_blyr['biological_year']).max()
df_max = df_max.reset_index()

# Summary table
## the month on which the maximum number of birds was recorded
df_summary = df_blyr[1:].groupby(['biological_year']).idxmax()
df_summary = (df_summary % 12) + 1
## the month on which the observation was cancelled
df_weath_summary = (df_weath[df_weath['weather_en'] == 'Cancelled']
                    .groupby(df_blyr['biological_year'])
                    .agg(cancelled_months=('date', lambda x: sorted(x.dt.month.unique())))
                    .reset_index())
## merge with summary
df_summary_show = df_summary.merge(df_weath_summary, on='biological_year', how='left')

# select species
species = df.columns[1:]
species = species.sort_values()
selected_species = st.multiselect('表示する種を選択してください.', species, default=list())

# make tabs to display plots
tab1, tab2, tab3, tab4 = st.tabs(["種ごとの年次推移", "年最大個体数", "最大個体数を観測した月", "種ごとの月別個体数"])

# display selected species data
with tab1: 
    if selected_species: 
        st.line_chart(df_max.set_index('biological_year')[selected_species])
    else: 
        st.info('表示する種を選択してください.')

with tab2: 
    if selected_species: 
        st.dataframe(df_max[['biological_year'] + selected_species])
    else: 
        st.info('表示する種を選択してください.')

with tab3: 
    if selected_species: 
        st.dataframe(df_summary_show[['biological_year', 'cancelled_months'] + selected_species])
        st.text('cancelled_monthsはその年で観測が中止された月を示します.')
    else: 
        st.info('表示する種を選択してください.')

with tab4: 
    if selected_species: 
        st.line_chart(df_blyr.set_index('date')[selected_species])
    else: 
        st.info('表示する種を選択してください.')
st.write('#')

# show datatable
with st.expander('データテーブルを表示'): 
    dt_tab1, dt_tab2, dt_tab3 = st.tabs(['月別個体数データ', '天候データ', '分類表'])
    with dt_tab1: 
        sp_show = st.multiselect('表示する種を選択してください.', species, default=list(), key = 'dt_tab1')
        st.dataframe(df_display[['date', 'weather_en'] + sp_show].style.applymap(bg.bg_cancelled, subset=['weather_en']))
    with dt_tab2: 
        st.dataframe(df_weath.style.applymap(bg.bg_cancelled, subset=['weather_en']))
        st.write('天候クラス')
        st.markdown('''
                    | Weather   | 天候    |
                    |-----------|--------|
                    | Clear   | 快晴   |
                    | Sunny   | 晴れ   |
                    | Cloudy  | 曇り   |
                    |LightRain| 少雨   |
                    | Snow    | 雪     |
                    |Cancelled| 中止   |
                    ''')
    with dt_tab3: 
        st.dataframe(df_tax)
        st.write('分類表は日本鳥類目録改訂第8版に準拠.')
        st.write('BirdTree列は鳥類系統樹のオープンデータベースであるBirdTree.org (2012) における分類群名.')
st.write('#')