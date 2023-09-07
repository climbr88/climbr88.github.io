from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import SelectField
import pandas as pd
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)
app.secret_key = '202eagle'  # Set your secret key

# Read the Excel sheet into a pandas dataframe
df = pd.read_excel('data/filename.xlsx', header=1)

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

# Define a function to update the chart when the customer dropdown changes
def update_chart(customer_name):
    files_data = customer_data[customer_name]['Files']
    teu_data = customer_data[customer_name]['TEU']
    files_customdata = [f'{year}' for year in files_data['Year']]
    teu_customdata = [f'{year}' for year in teu_data['Year']]
    fig_files = px.line(files_data, x='Month', y='Files', color='Year', title=f'{customer_name} Files by Month')
    fig_files.update_traces(mode='lines+markers', hovertemplate='Month: %{x}<br>Files: %{y}<br>Year: %{customdata}<extra></extra>', customdata=files_customdata)
    fig_files.update_layout(yaxis_title='Number of Files', hovermode='closest', xaxis=dict(showticklabels=True))
    fig_files.update_xaxes(tickvals=list(range(1, 13)), ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    fig_files.update_yaxes(showticklabels=False, tickmode='linear', dtick=1)
    fig_teu = px.line(teu_data, x='Month', y='TEU', color='Year', title=f'{customer_name} TEU by Month')
    fig_teu.update_traces(mode='lines+markers', hovertemplate='Month: %{x}<br>TEU: %{y}<br>Year: %{customdata}<extra></extra>', customdata=teu_customdata)
    fig_teu.update_layout(yaxis_title='Number of TEU', hovermode='closest', xaxis=dict(showticklabels=True))
    fig_teu.update_xaxes(tickvals=list(range(1, 13)), ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    fig_teu.update_yaxes(showticklabels=False, tickmode='linear', dtick=1)
    
    # Export the chart as an HTML file
    files_html = pio.to_html(fig_files, full_html=False)
    teu_html = pio.to_html(fig_teu, full_html=False)
    return files_html, teu_html

class CustomerForm(FlaskForm):
    customer = SelectField('Select Customer', choices=[], coerce=str)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = CustomerForm()

    # Populate the choices for the dropdown from customer_data
    form.customer.choices = [(customer, customer) for customer in customer_data.keys()]
    

    if form.validate_on_submit():
        customer_name = form.customer.data
        files_html, teu_html = update_chart(customer_name)
        return render_template('index.html', form=form, files_html=files_html, teu_html=teu_html)
    else:
        return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
