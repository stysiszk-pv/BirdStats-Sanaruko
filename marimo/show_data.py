import marimo

__generated_with = "0.16.5"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""Test code to show number of observed bird species for given one year range.""")
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import pandas as pd
    return (pd,)


@app.cell
def _():
    import os
    return (os,)


@app.cell
def _(os):
    os.getcwd()
    return


@app.cell
def _():
    import matplotlib.pyplot as plt
    import seaborn as sns
    return plt, sns


@app.cell
def _(pd):
    # read excel file
    df = pd.read_excel('data/Bird_Sanaruko.xlsx', sheet_name = 'obs_df')
    # convert date to datetime
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    return (df,)


@app.cell
def _(pd):
    ##SpeciesID as column names
    df_spID = pd.read_excel('data/Bird_Sanaruko.xlsx', sheet_name = 'ObsTable')
    df_spID['date'] = pd.to_datetime(df_spID['date'], format='%Y%m%d')
    return


@app.cell
def _(pd):
    ##Taxonomy table
    df_tax = pd.read_excel('data/Bird_Sanaruko.xlsx', sheet_name = 'TaxTable')
    return


@app.cell
def _(pd):
    ##Weather table
    df_weath = pd.read_excel('data/Bird_Sanaruko.xlsx', sheet_name = 'weather')
    df_weath['date'] = pd.to_datetime(df_weath['date'], format='%Y%m%d')
    return (df_weath,)


@app.cell
def _(df, df_weath):
    # merge weather and observation data
    df_display = df_weath.merge(df, on='date', how='left')
    return (df_display,)


@app.cell
def _(df_display):
    df_display
    return


@app.cell
def _(df_display):
    # Exclude 'date' and 'weather_en' columns and stack the dataframe
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

    # Display the stacked dataframe
    stacked_df.head(10)
    return (stacked_df,)


@app.cell
def _(stacked_df):
    # Extract month from date and create a new column
    stacked_df['month'] = stacked_df['date'].dt.strftime('%Y-%m')

    # Group by month and Species, then sum the Count
    monthly_species_counts = stacked_df.groupby(['month', 'Species'])['Count'].sum().reset_index()

    # Remove entries with zero counts
    monthly_species_counts = monthly_species_counts[monthly_species_counts['Count'] > 0]

    monthly_species_counts
    return (monthly_species_counts,)


@app.cell
def _(monthly_species_counts):
    # Count unique species per month
    species_per_month = monthly_species_counts.groupby('month')['Species'].nunique().reset_index()
    species_per_month.columns = ['Month', 'Number of Species']
    return (species_per_month,)


@app.cell
def _(mo, species_per_month):
    # Create pulldown selectors for start year and month
    unique_months = sorted(species_per_month['Month'].unique())

    # Extract unique years and months from the data
    years = sorted(set(month.split('-')[0] for month in unique_months))
    months_list = [(i, f"{i:02d}") for i in range(1, 13)]  # (value, label) pairs

    # Default to the same year/month as in the original selector (months[-12])
    default_year, default_month = unique_months[-12].split('-')

    # Create separate dropdowns for year and month
    year_selector = mo.ui.dropdown(
        options=years,
        value=default_year,
        label="Year"
    )

    month_selector = mo.ui.dropdown(
        options=[m[1] for m in months_list],
        value=default_month,
        label="Start Month"
    )

    # Display selectors side by side
    mo.hstack([year_selector, month_selector], justify="start")
    return month_selector, year_selector


@app.cell(hide_code=True)
def _(month_selector, species_per_month, year_selector):
    # Filter species_per_month based on the selected month range
    # Calculate end month (one year after start month)
    year = int(year_selector.value)
    month = int(month_selector.value)
    start_month_str = f"{year}-{month:02d}"

    # Calculate end month (should be 11 months after start month for a 12-month period)
    end_month = month - 1 if month > 1 else 12
    end_year = year + 1 if month != 1 else year
    end_month_str = f"{end_year}-{end_month:02d}"

    # Filter the data
    filtered_species_per_month = species_per_month[
        (species_per_month['Month'] >= start_month_str) & 
        (species_per_month['Month'] <= end_month_str)
    ]
    return end_month_str, filtered_species_per_month, start_month_str


@app.cell(hide_code=True)
def _(end_month_str, filtered_species_per_month, plt, sns, start_month_str):
    # Create a figure with appropriate size
    plt.figure(figsize=(12, 6))

    # Create a bar chart using Seaborn with fixed palette warning
    ax = sns.barplot(
        data=filtered_species_per_month,
        x='Month',
        y='Number of Species',
        hue='Month',  # Assign x variable to hue
        palette='viridis',
        legend=False  # Hide the legend
    )

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')

    # Add text labels on top of bars
    for i, row in enumerate(filtered_species_per_month.itertuples()):
        plt.text(
            i, 
            row._2 + 0.5,  # Add a small offset above the bar
            str(row._2),   # The value to display
            ha='center'
        )

    # Add title and labels
    plt.title(f'Number of Bird Species from {start_month_str} to {end_month_str}')
    plt.xlabel('Month')
    plt.ylabel('Number of Unique Species')
    plt.tight_layout()  # Adjust layout to make room for labels

    # Return the current axes as required
    plt.gca()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
