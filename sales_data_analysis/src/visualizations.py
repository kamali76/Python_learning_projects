import os
import matplotlib.pyplot as plt
import seaborn as sns

# Directory where all generated charts will be saved
OUTPUT_DIR = "sales_data_analysis/outputs/charts"

# Create the output directory if it does not already exist
os.makedirs(OUTPUT_DIR, exist_ok=True)


def plot_monthly_sales(monthly_sales):
    """
    Generates and saves a line chart showing total sales aggregated by month.
    Parameters:
        monthly_sales (pd.Series): Monthly aggregated sales values
    """
    # Create a new figure to avoid overlap with other plots
    plt.figure(figsize=(10, 5))

    # Plot monthly sales trend
    monthly_sales.plot(kind='line')

    # Add chart title and axis labels
    plt.title("Monthly Sales Revenue")
    plt.xlabel("Month")
    plt.ylabel("Total Sales")

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Save the plot as an image file
    file_path = os.path.join(OUTPUT_DIR, "monthly_sales_trend.png")
    plt.savefig(file_path)

    # Display the plot
    plt.show()


def plot_top_categories(category_sales):
    """
    Generates and saves a bar chart showing top product categories by revenue.
    Parameters:
        category_sales (pd.Series): Revenue aggregated by product category
    """
    # Create a new figure for the bar chart
    plt.figure(figsize=(10, 6))

    # Create horizontal bar chart for better readability
    sns.barplot(
        x=category_sales.values,
        y=category_sales.index
    )

    # Add chart title and axis labels
    plt.title("Top Product Categories by Revenue")
    plt.xlabel("Total Sales")
    plt.ylabel("Category")

    # Adjust layout spacing
    plt.tight_layout()

    # Save the plot as an image file
    file_path = os.path.join(OUTPUT_DIR, "top_categories_by_revenue.png")
    plt.savefig(file_path)

    # Display the plot
    plt.show()
