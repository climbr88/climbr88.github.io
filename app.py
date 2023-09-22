from flask import Flask, render_template
import pandas as pd
import os

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

# Identify customers with a decrease of 20% or more in shipments in 2023 compared to 2022
decrease_customers = []
for customer in files_by_customer['CUSTOMER'].unique():
    files_2022 = files_by_customer[(files_by_customer['CUSTOMER'] == customer) & (files_by_customer['Year'] == 2022)]['Files'].sum()
    files_q1_2023 = files_by_customer[(files_by_customer['CUSTOMER'] == customer) & (files_by_customer['Year'] == 2023) & (files_by_customer['Month'] <= 3)]['Files'].sum()
    files_q2_2023 = files_by_customer[(files_by_customer['CUSTOMER'] == customer) & (files_by_customer['Year'] == 2023) & (files_by_customer['Month'] <= 6)]['Files'].sum()
    total_files_2022 = files_by_customer[(files_by_customer['CUSTOMER'] == customer) & (files_by_customer['Year'] == 2022)]['Files'].sum()
    total_files_2023 = files_by_customer[(files_by_customer['CUSTOMER'] == customer) & (files_by_customer['Year'] == 2023)]['Files'].sum()
    teu_2022 = teu_by_customer[(teu_by_customer['CUSTOMER'] == customer) & (teu_by_customer['Year'] == 2022)]['TEU'].sum()
    teu_q1_2023 = teu_by_customer[(teu_by_customer['CUSTOMER'] == customer) & (teu_by_customer['Year'] == 2023) & (teu_by_customer['Month'] <= 3)]['TEU'].sum()
    teu_q2_2023 = teu_by_customer[(teu_by_customer['CUSTOMER'] == customer) & (teu_by_customer['Year'] == 2023) & (teu_by_customer['Month'] <= 6)]['TEU'].sum()
    total_teu_2022 = teu_by_customer[(teu_by_customer['CUSTOMER'] == customer) & (teu_by_customer['Year'] == 2022)]['TEU'].sum()
    total_teu_2023 = teu_by_customer[(teu_by_customer['CUSTOMER'] == customer) & (teu_by_customer['Year'] == 2023)]['TEU'].sum()
    
    decrease_files_q2_to_q1 = (files_q1_2023 - files_q2_2023) / files_q1_2023 * 100
    decrease_teu_q2_to_q1 = (teu_q1_2023 - teu_q2_2023) / teu_q1_2023 * 100

    
    if files_2022 > 0 and (files_q2_2023 / files_2022) <= 0.8:
        percent_decrease_files = ((files_2022 - files_q2_2023) / files_2022) * 100
    else:
        percent_decrease_files = None

    if teu_2022 > 0 and (teu_q2_2023 / teu_2022) <= 0.8:
        percent_decrease_teu = ((teu_2022 - teu_q2_2023) / teu_2022) * 100
    else:
        percent_decrease_teu = None
    
    if percent_decrease_files is not None or percent_decrease_teu is not None:
        decrease_customers.append((customer, total_files_2022, total_files_2023, percent_decrease_files, total_teu_2022, total_teu_2023, percent_decrease_teu, files_q1_2023, files_q2_2023, decrease_files_q2_to_q1, teu_q1_2023, teu_q2_2023, decrease_teu_q2_to_q1))

decrease_customers = sorted(decrease_customers, reverse=True, key=lambda x: x[1] if x[1] is not None else -1)

# Define a route to render the index.html template
@app.route('/')
def index2():
    return render_template('index2.html', decrease_customers=decrease_customers)

if __name__ == '__main__':
    app.run(debug=True)
