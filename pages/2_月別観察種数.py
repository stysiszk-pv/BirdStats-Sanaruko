import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import platform
import sys
import os

# モジュールの検索パスにスクリプトのディレクトリを追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts import data_loader


st.set_page_config(page_title="月別観察種数", page_icon="📈")

# 日本語フォントの設定
def setup_japanese_fonts():
    # まずローカルのフォントを試す
    font_candidates = ['Noto Sans JP','Noto Sans CJK JP', 'IPAexGothic', 'MS Gothic', 'Yu Gothic']
    # font_candidates = ['IPAexGothic', 'Yu Gothic']
    available_fonts = []
    
    for font_name in font_candidates:
        try:
            fp = fm.FontProperties(family=[font_name])
            fn = fm.findfont(fp)
            # 実際にフォントファイルが存在し、デフォルトのフォントでないことを確認
            if os.path.exists(fn) and not fn.endswith('DejaVuSans.ttf'):
                available_fonts.append(font_name)
                print(f"フォントが見つかりました: {font_name} ({fn})")
            else:
                print(f"フォント {font_name} は利用できません")
        except Exception as e:
            print(f"フォント {font_name} は利用できません: {str(e)}")
    
    if not available_fonts:
        # ローカルフォントが見つからない場合、Noto Sans JPをダウンロード
        try:
            import urllib.request
            import tempfile
            
            # Noto Sans JP フォントをダウンロード
            FONT_URL = "https://github.com/google/fonts/raw/main/ofl/notosansjp/NotoSansJP%5Bwght%5D.ttf"
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.otf') as tf:
                with urllib.request.urlopen(FONT_URL) as response:
                    tf.write(response.read())
                font_path = tf.name
            
            # ダウンロードしたフォントを登録
            fm.fontManager.addfont(font_path)
            available_fonts = ['Noto Sans JP']
            print("日本語フォントNoto Sans JPをダウンロードしました")
        except Exception as e:
            st.warning(f"フォントのダウンロードに失敗しました: {e}")
    
    # フォント設定を適用
    if available_fonts:
        plt.rcParams['font.family'] = available_fonts
    else:
        plt.rcParams['font.family'] = ['sans-serif']

# フォント設定を実行
setup_japanese_fonts()

st.title('月ごとの観察種数の推移')
st.write('#####  浜松野鳥の会')

# データの読み込み
df_display, _ , _ , _= data_loader.load_bird_data()

# データの整形
columns_to_keep_as_id = ['date', 'weather_en']
value_columns = [col for col in df_display.columns if col not in columns_to_keep_as_id]

# Stack the dataframe
stacked_df = df_display.melt(
    id_vars=columns_to_keep_as_id,
    value_vars=value_columns,
    var_name='Species',
    value_name='Count'
)

# Remove rows with missing values
stacked_df = stacked_df.dropna(subset=['Count'])

# Extract month from date and create a new column
stacked_df['month'] = stacked_df['date'].dt.strftime('%Y-%m')

# Group by month and Species, then sum the Count
monthly_species_counts = stacked_df.groupby(['month', 'Species'])['Count'].sum().reset_index()

# Remove entries with zero counts
monthly_species_counts = monthly_species_counts[monthly_species_counts['Count'] > 0]

# Count unique species per month
species_per_month = monthly_species_counts.groupby('month')['Species'].nunique().reset_index()
species_per_month.columns = ['Month', 'Number of Species']

with st.expander('このページの使い方', expanded=True):
    st.markdown('''
    このページでは、月ごとの観察種数の推移を確認できます。

    1. 年を選択
    2. 開始月を選択
    3. グラフには選択した月から1年間の観察種数が表示されます
    4. データテーブルを展開すると、詳細な数値を確認できます
    ''')

# 期間選択のUIを作成
unique_months = sorted(species_per_month['Month'].unique())
years = sorted(set(month.split('-')[0] for month in unique_months), reverse=True)  # 新しい年から古い年の順

# デフォルト値を設定（最新の年から12ヶ月前）
default_year, default_month = unique_months[-12].split('-')

col1, col2 = st.columns(2)
with col1:
    year = st.selectbox("年を選択", options=years, index=years.index(default_year))
with col2:
    month = st.selectbox("開始月を選択", options=range(1, 13), index=int(default_month)-1, format_func=lambda x: f"{x:02d}")

# 選択された期間に基づいてデータをフィルタリング
start_month_str = f"{year}-{month:02d}"

# 終了月を計算（12ヶ月後の前月）
end_month = month - 1 if month > 1 else 12
end_year = str(int(year) + 1) if month != 1 else year
end_month_str = f"{end_year}-{end_month:02d}"

# データのフィルタリング
filtered_species_per_month = species_per_month[
    (species_per_month['Month'] >= start_month_str) & 
    (species_per_month['Month'] <= end_month_str)
]

# グラフの作成
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(
    data=filtered_species_per_month,
    x='Month',
    y='Number of Species',
    hue='Month',
    palette='viridis',
    legend=False,
    ax=ax
)

# グラフの装飾
plt.xticks(rotation=45, ha='right')
for i, row in enumerate(filtered_species_per_month.itertuples()):
    plt.text(
        i, 
        row._2 + 0.5,
        str(row._2),
        ha='center'
    )

plt.title(f'月ごとの観察種数 ({start_month_str} から {end_month_str})')
plt.xlabel('月')
plt.ylabel('観察種数')
plt.tight_layout()

# Streamlitでグラフを表示
st.pyplot(fig)

# データテーブルも表示
with st.expander("データテーブルを表示"):
    st.dataframe(filtered_species_per_month)