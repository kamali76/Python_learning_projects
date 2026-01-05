from load_data import load_sales_data
from clean_data import clean_sales_data
from analysis import get_monthly_sales, get_top_categories
from visualizations import plot_monthly_sales, plot_top_categories

df = load_sales_data("sales_data_analysis/data/customer_shopping_data.csv")
df = clean_sales_data(df)

monthly_sales = get_monthly_sales(df)
top_categories = get_top_categories(df)

plot_monthly_sales(monthly_sales)
plot_top_categories(top_categories)