import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def main():
    st.title('月ごとの観察種数の推移')
    
    # read excel file
    df = pd.read_excel('data/Bird_Sanaruko.xlsx', sheet_name='obs_df')
    df_weath = pd.read_excel('data/Bird_Sanaruko.xlsx', sheet_name='weather')

    # convert date to datetime
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    df_weath['date'] = pd.to_datetime(df_weath['date'], format='%Y%m%d')

    # merge weather and observation data
    df_display = df_weath.merge(df, on='date', how='left')

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

    # 期間選択のUIを作成
    unique_months = sorted(species_per_month['Month'].unique())
    years = sorted(set(month.split('-')[0] for month in unique_months))
    
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

if __name__ == "__main__":
    main()