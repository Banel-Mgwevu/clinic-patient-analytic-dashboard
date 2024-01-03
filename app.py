from flask import Flask, render_template
import mysql.connector
import plotly.graph_objs as go
import json
import re
from datetime import datetime, timedelta
import calendar

app = Flask(__name__)

# MySQL configurations
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'patientsdb'
}

# Function to test MySQL connection
def test_mysql_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        if conn.is_connected():
            print('Connected to MySQL database')
            return True, conn
        else:
            return False, None
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return False, None

def parse_custom_date(date_str):
    month_match = re.match(r'([a-zA-Z]+)(\d+)', date_str)
    if month_match:
        month_str = month_match.group(1)
        year_str = month_match.group(2)
        month_num = list(calendar.month_abbr).index(month_str.capitalize()[:3])
        return datetime.strptime(f'01-{month_num:02d}-{year_str}', '%d-%m-%Y')
    else:
        return None  
# Route to display data on the main dashboard
@app.route('/')
def display_data():
    connected, connection = test_mysql_connection()

    if connected:
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM patienthealthrecords"
            cursor.execute(query)
            data = cursor.fetchall()

            return render_template('dashboard.html', data=data)

        except mysql.connector.Error as e:
            return f"Error executing query: {e}"

    else:
        return 'Failed to connect to MySQL'


# ... (previous code remains unchanged)

# Route for displaying detailed view of a specific patient







@app.route('/details/<patient_id>')
def patient_details(patient_id):
    connected, connection = test_mysql_connection()

    if connected:
        try:
            cursor = connection.cursor(dictionary=True)
            query = f"SELECT * FROM patienthealthrecords WHERE PatientId = '{patient_id}'"
            cursor.execute(query)
            data = cursor.fetchone()  # Fetch single row for the patient ID

            if data:
                # Extracting data from the database
                diastolic_bp = data.get('DiastolicBP', '[]')
                SystolicBP_bp = data.get('SystolicBP', '[]')
                Height_bp = data.get('Height', '[]')
                Weight_bp = data.get('Weight', '[]')
                BloodGlucose_bp = data.get('BloodGlucose', '[]')
                Date_dp = data.get('Date', '[]')
                cd = data.get('CD4CountResults', '[]')
                date_of_hiv_diagnosis = data.get('DateofHIVDiagnosis')
                year_of_hiv_diagnosis = data.get('YearOfHIVDiagnosis')
                diagnosis1 = data.get('diagnosis1')
                unique_values = set(diagnosis1)
                for value in unique_values:
                 print(value)
                


               
                


                # Process and clean the data for the charts
                diastolic_bp_cleaned = [int(x) for x in re.findall(r'\d+', diastolic_bp)]
                SystolicBP_cleaned = [int(x) for x in re.findall(r'\d+', SystolicBP_bp)]
                Height_bp_cleaned = [int(x) for x in re.findall(r'\d+', Height_bp)]
                Weight_bp_cleaned = [float(x) for x in re.findall(r'\d+', Weight_bp)]
                BloodGlucose_bp_bp = [int(x) for x in re.findall(r'\d+', BloodGlucose_bp)]
                

                
                # Process and sort the date data
                dates = re.findall(r'[a-zA-Z]+\d+', Date_dp)
                formatted_dates = [parse_custom_date(date).strftime('%Y-%m-%d') for date in dates]
                sorted_dates = sorted(formatted_dates)
                
                # Check if any of the data is empty
                if diastolic_bp_cleaned or SystolicBP_cleaned or Height_bp_cleaned or Weight_bp_cleaned or BloodGlucose_bp_bp:
                    return render_template('details.html', patient=data,
                                           diastolic_bp=diastolic_bp_cleaned,
                                           SystolicBP_bp=SystolicBP_cleaned,
                                           Height_bp=Height_bp_cleaned,
                                           Weight_bp=Weight_bp_cleaned,
                                           BloodGlucose_bp=BloodGlucose_bp_bp,
                                           Date_v=sorted_dates,
                                           date_of_hiv_diagnosis=date_of_hiv_diagnosis,
                                           year_of_hiv_diagnosis=year_of_hiv_diagnosis,
                                           cd=cd)  # Pass sorted dates to the template
                else:
                    return 'No valid data available for the charts'

            else:
                return 'Patient not found'

        except mysql.connector.Error as e:
            return f"Error retrieving patient details: {e}"

    else:
        return 'Failed to connect to MySQL'


if __name__ == '__main__':
    app.run(debug=True)
