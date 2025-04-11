from flask import Flask, render_template, request, send_file
from datetime import datetime
import csv, os, socket
import pandas as pd
import qrcode

app = Flask(__name__)
CSV_FILE = "attendance.csv"

def get_client_info(req):
    ip = request.remote_addr
    device = request.user_agent.string
    return ip, device

def generate_qr(url):
    img = qrcode.make(url)
    img.save("static/qr.png")

@app.route("/", methods=["GET", "POST"])
def index():
    submitted = False
    if request.method == "POST":
        name = request.form["name"]
        reg = request.form["reg"]
        date = datetime.now().strftime("%Y-%m-%d")
        time = datetime.now().strftime("%H:%M:%S")
        ip, device = get_client_info(request)

        new_row = [name, reg, date, time, ip, device]
        repeated = check_duplicate_today(new_row)

        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(new_row)

        submitted = True

    return render_template("index.html", submitted=submitted)

def check_duplicate_today(row):
    if not os.path.exists(CSV_FILE):
        return False

    df = pd.read_csv(CSV_FILE)
    name, reg, date, _, ip, device = row
    today_df = df[df["Date"] == date]
    match = today_df[(today_df["Name"] == name) & (today_df["RegNo"] == reg)]
    return not match.empty

@app.route("/admin")
def admin():
    if not os.path.exists(CSV_FILE):
        return "No records yet."

    df = pd.read_csv(CSV_FILE)
    today = datetime.now().strftime("%Y-%m-%d")
    today_df = df[df["Date"] == today]
    duplicated = today_df.duplicated(subset=["Name", "RegNo"], keep='first')
    today_df["Duplicate"] = duplicated
    return render_template("admin.html", records=today_df.to_dict(orient="records"))

@app.route("/download")
def download():
    return send_file(CSV_FILE, as_attachment=True)

if __name__ == "__main__":
    ip_address = socket.gethostbyname(socket.gethostname())
    generate_qr(f"http://{ip_address}:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
