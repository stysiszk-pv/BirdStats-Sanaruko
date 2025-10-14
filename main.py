import streamlit as st

st.set_page_config(
    page_title="BirdStats Sanaruko",
    page_icon="🦜",
    layout="wide"
)

st.title("BirdStats Sanaruko: 佐鳴湖における鳥類個体数の推移")
st.write("#####  浜松野鳥の会")

st.write('###')
with st.expander('概要', expanded=True):
    st.markdown("浜松野鳥の会は1982年から現在まで, 佐鳴湖に生息する鳥類の個体数を目視観測により毎月記録してきました. " \
    "  \n40年近くにわたる詳細な鳥類群集データが, 更に広く共有され受け継がれることを願い, 有志会員の手により, 観測記録のデジタル化が進められています (2020年まで完了, 2025/08/29現在).")
    
    st.markdown("### 機能")
    st.markdown("""
    このアプリケーションでは以下の機能を提供しています：
    
    1. 種ごとの年間最大個体数の推移（種別個体数ページ）
        - 種ごとの個体数の年次推移
        - 年最大個体数のデータ表示
        - 最大個体数を観測した月の表示
        - 種ごとの月別個体数の表示
        
    2. 月ごとの観察種数の推移（月別観察種数ページ）
        - 指定した期間の月ごとの観察種数をグラフ表示
        - データテーブルの表示
    """)
    
    st.markdown("---")
    st.markdown("Source code及びデータはGitHubにて公開しています：")
    st.markdown("[BirdStats-Sanaruko GitHub Repository](https://github.com/stysiszk-pv/BirdStats-Sanaruko.git)")

st.write('#')
st.text('This page was made by S.I. modified by Y.I. with Claude')
st.text('Last updated: 2025/10/03')