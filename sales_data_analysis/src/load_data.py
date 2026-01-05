import pandas as pd

def load_sales_data(file_path):
    """
    Loads customer shopping dataset from CSV file.
    """
    df = pd.read_csv(file_path)
    return df


if __name__ == "__main__":
    df = load_sales_data("sales_data_analysis/data/customer_shopping_data.csv")
    print(df.head())
    print(df.info())