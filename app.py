from flask import Flask, render_template, request, redirect
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

attendance_file = "attendance.csv"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    regno = request.form['regno']
    date = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')

    # Prepare new row
    new_entry = {
        "Name": name,
        "RegNo": regno,
        "Date": date,
        "Time": time,
        "IP": ip,
        "Device": user_agent
    }

    # Create file with header if not exists
    if not os.path.exists(attendance_file):
        df = pd.DataFrame(columns=["Name", "RegNo", "Date", "Time", "IP", "Device"])
        df.to_csv(attendance_file, index=False)

    # Append entry
    df = pd.read_csv(attendance_file)
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(attendance_file, index=False)

    return render_template('success.html', name=name)

@app.route('/admin')
def admin():
    if not os.path.exists(attendance_file):
        return "No attendance data found."

    df = pd.read_csv(attendance_file)
    today = datetime.now().strftime("%Y-%m-%d")

    if "Date" not in df.columns:
        return "Error: 'Date' column not found in the CSV. Please check your file."

    today_df = df[df["Date"] == today]

    return render_template('admin.html', data=today_df.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)
