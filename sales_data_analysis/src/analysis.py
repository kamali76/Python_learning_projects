def get_monthly_sales(df):
    return df.groupby(df['invoice_date'].dt.to_period('M'))['total_sales'].sum()


def get_top_categories(df, top_n=10):
    return (
        df.groupby('category')['total_sales']
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
    )