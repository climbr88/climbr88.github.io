!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Customer Data Visualization</title>
    <!-- Add any necessary CSS stylesheets or Bootstrap here -->
    <!-- For example, you can include Bootstrap CSS by adding the following line: -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"> -->
</head>
<body>
    <h1>Chart for {{ request.form['customer_name'] }}</h1>
    <div>
        {{ fig_files_html | safe }}
    </div>
    <div>
        {{ fig_teu_html | safe }}
    </div>
    <div class="container">
        <h1>2022 v 2023 by File and TEU</h1>
        <form method="POST" class="form-inline">
            {{ form.hidden_tag() }}
            <div class="row">
                <div class="col-sm-8">
                    <div class="form-group">
                        {{ form.customer.label }}
                        {{ form.customer(class="form-control") }}
                    </div>
                </div>
                <div class="col-sm-4">
                    <button type="submit" class="btn btn-primary mt-4">Submit</button>
                </div>
            </div>
        </form>
        <div class="chart">
            <!-- Display the Files chart here -->
            {{ files_html | safe }}
        </div>
        <div class="chart">
            <!-- Display the TEU chart here -->
            {{ teu_html | safe }}
        </div>
    </div>
    <!-- Add any necessary JavaScript libraries or scripts here -->
</body>
</html>
