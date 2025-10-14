import pandas as pd

def load_bird_data():
    """
    鳥類観察データの基本的な読み込みと前処理を行う関数
    
    Returns:
        tuple: (df_display, df_tax)
            - df_display: 観察データと天候データを結合したDataFrame
            - df_tax: 分類表のDataFrame
    """
    # 基本データの読み込み
    df = pd.read_excel('data/Bird_Sanaruko.xlsx', sheet_name='obs_df')
    df_tax = pd.read_excel('data/Bird_Sanaruko.xlsx', sheet_name='TaxTable')
    df_weath = pd.read_excel('data/Bird_Sanaruko.xlsx', sheet_name='weather')

    # 日付のdatetime変換
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    df_weath['date'] = pd.to_datetime(df_weath['date'], format='%Y%m%d')

    # 観察データと天候データの結合
    df_display = df_weath.merge(df, on='date', how='left')

    return df_display, df_tax, df_weath,df