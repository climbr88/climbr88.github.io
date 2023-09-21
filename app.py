from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)
app.secret_key = '202eagle'  # Set your secret key

# Read the Excel sheet into a pandas dataframe
df = pd.read_excel('static/filename.xlsx', header=1)

# Convert the date columns to datetime format
df['ETA'] = pd.to_datetime(df['ETA'])
df['DISCHARGE DATE'] = pd.to_datetime(df['DISCHARGE DATE'])
df['ACTUAL ARRIVAL DATE'] = pd.to_datetime(df['ACTUAL ARRIVAL DATE'])

# Add columns for month and year
df['Month'] = df['ETA'].dt.month
df['Year'] = df['ETA'].dt.year

# Group by customer, month, and year and aggregate the counts
files_by_customer = df.groupby(['CUSTOMER', 'Month', 'Year'])['FILE'].count().reset_index(name='Files')
teu_by_customer = df.groupby(['CUSTOMER', 'Month', 'Year'])['TEU'].sum().reset_index(name='TEU')

# Filter out customers with less than 10 total files
files_by_customer = files_by_customer.groupby('CUSTOMER').filter(lambda x: x['Files'].sum() >= 10)

# Create a dictionary of customers and their data
customer_data = {}
for customer in files_by_customer['CUSTOMER'].unique():
    files_data = files_by_customer[files_by_customer['CUSTOMER'] == customer]
    teu_data = teu_by_customer[teu_by_customer['CUSTOMER'] == customer]
    customer_data[customer] = {'Files': files_data, 'TEU': teu_data}

# Calculate total files and TEU for Jan-Aug 2022 and 2023
total_files_2022 = files_by_customer[(files_by_customer['Year'] == 2022) & (files_by_customer['Month'] <= 8)].groupby('CUSTOMER')['Files'].sum()
total_files_2023 = files_by_customer[(files_by_customer['Year'] == 2023) & (files_by_customer['Month'] <= 8)].groupby('CUSTOMER')['Files'].sum()

total_teu_2022 = teu_by_customer[(teu_by_customer['Year'] == 2022) & (teu_by_customer['Month'] <= 8)].groupby('CUSTOMER')['TEU'].sum()
total_teu_2023 = teu_by_customer[(teu_by_customer['Year'] == 2023) & (teu_by_customer['Month'] <= 8)].groupby('CUSTOMER')['TEU'].sum()

# Calculate percent decrease
decrease_customers = []
for customer in total_files_2022.index:
    percent_decrease_files = ((total_files_2022[customer] - total_files_2023.get(customer, 0)) / total_files_2022[customer]) * 100
    percent_decrease_teu = ((total_teu_2022[customer] - total_teu_2023.get(customer, 0)) / total_teu_2022[customer]) * 100
    if percent_decrease_files >= 20 or percent_decrease_teu >= 20:
        decrease_customers.append((customer, percent_decrease_files, percent_decrease_teu, total_files_2022[customer], total_files_2023.get(customer, 0), total_teu_2022[customer], total_teu_2023.get(customer, 0)))

# Sort the list by the highest decrease in volume first
decrease_customers = sorted(decrease_customers, key=lambda x: x[1], reverse=True)

@app.route('/')
def index2():
    return render_template('index2.html', decrease_customers=decrease_customers, customer_data=customer_data)

if __name__ == '__main__':
    app.run(debug=True)
