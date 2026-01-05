import pandas as pd

def clean_sales_data(df):
    """
    Cleans raw sales data:
    - removes duplicates
    - converts invoice_date to datetime
    - creates total_sales column
    """
    df = df.drop_duplicates()

    df['invoice_date'] = pd.to_datetime(
        df['invoice_date'],
        dayfirst=True
    )

    df['total_sales'] = df['price'] * df['quantity']
    return df
