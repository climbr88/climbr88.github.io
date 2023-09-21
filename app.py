from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

# Load the Excel file
df = pd.read_excel('static/cl_p&l_2023.xlsx', header=7)  # Assuming your data starts from row 8

# Convert 'ETA DATE' column to datetime format
df['ETA DATE'] = pd.to_datetime(df['ETA DATE'])

# Extract month and year from 'ETA DATE'
df['Month'] = df['ETA DATE'].dt.month
df['Year'] = df['ETA DATE'].dt.year

# Calculate the count of files per customer
customer_file_count = df.groupby('CUSTOMER NAME')['FILE NO'].transform('nunique')

# Filter out customers with less than 10 files
df_filtered = df[customer_file_count >= 10]

# Calculate the total profit by customer
total_profit_per_customer = df_filtered.groupby('CUSTOMER NAME')['PROFIT'].sum()

# Calculate the total number of files per customer
total_files_per_customer = df_filtered.groupby('CUSTOMER NAME')['FILE NO'].nunique()

# Calculate the average profit per file for each customer
average_profit_per_file = total_profit_per_customer / total_files_per_customer

# Format the profit values to two decimal places
total_profit_per_customer = total_profit_per_customer.round(2)
average_profit_per_file = average_profit_per_file.round(2)
# Routes to display tables

# Routes to display the updated table
@app.route('/')
def index():
    # Prepare data for the table
    data = pd.DataFrame({
        'Customer Name': total_profit_per_customer.index,
        'Total Profit': total_profit_per_customer.values,
        'Total Files': total_files_per_customer.values,
        'Profit Per File': average_profit_per_file.values
    })

    # Render the updated index.html template with the data
    return render_template('index.html', data=data)
if __name__ == '__main__':
    app.run(debug=True)



