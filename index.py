from flask import Flask, render_template, request, redirect, session, url_for
from flask_mail import Mail, Message
import json
import sqlite3
import os
from dotenv import load_dotenv
import threading
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import random

load_dotenv()
        
app = Flask(__name__)

@app.context_processor
def inject_stage_and_region():
    return dict(domain=os.getenv('Domain_OR_IP'))
    
app.secret_key = os.getenv('APP_SECRET_KEY')

recipients = [recipient.strip() for recipient in os.getenv('APPLICATION_RECIPIENTS').split(',')]

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_TLS')
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)
   
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(msg):
    thr = threading.Thread(target=send_async_email, args=[app, msg])
    thr.start()
         
# Load the credentials for the service account
credentials = service_account.Credentials.from_service_account_file(
    os.getenv('SERVICE_ACCOUNT_JSON'),
    scopes=['https://www.googleapis.com/auth/calendar']
)
service = build('calendar', 'v3', credentials=credentials)

def create_database():
    if not os.path.exists('leave_applications.db'):
        conn = sqlite3.connect('leave_applications.db')
        c = conn.cursor()
        c.execute("CREATE TABLE leave_applications (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, leave_days TEXT, leave_period TEXT,  reason TEXT, status TEXT)")
        c.execute("CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, password TEXT)")
        c.execute("INSERT INTO users (email, password) Values (?,?)",(os.getenv('DEFAULT_USER'),os.getenv('DEFAULT_USER_PASSWORD')))
        conn.commit()
        conn.close()

create_database()

def get_db():
    conn = sqlite3.connect('leave_applications.db')
    conn.row_factory = sqlite3.Row
    return conn

# function to update the leave request status
def update_status(email, status):
    conn = get_db()
    conn.execute('UPDATE leave_applications SET status = ? WHERE email = ?', [status, email])
    conn.commit()
    conn.close()
    
def get_status(email):
    conn = get_db()
    cursor = conn.cursor()
    status = cursor.execute('Select status from leave_applications WHERE email = ?', [email])
    row = cursor.fetchone()
    conn.close()
    return(row[0])
    
def get_dates(email):
    conn = get_db()
    cursor = conn.cursor()
    status = cursor.execute('Select leave_period from leave_applications WHERE email = ?', [email])
    row = cursor.fetchone()
    conn.close()
    return(row[0])
    
def get_leave_rec(email):
    conn = get_db()
    cursor = conn.cursor()
    status = cursor.execute('Select * from leave_applications WHERE email = ?', [email])
    row = cursor.fetchone()
    conn.close()
    return(row)    

def create_event(name, start_date, end_date, reason, service):
        start_date = datetime.strptime(start_date, '%d-%m-%Y')
        end_date = datetime.strptime(end_date, '%d-%m-%Y')
        event = {
            'summary': name+" is on Leave",
            'description': reason,
            'colorId': random.choice(['1','2','3','4','5','6','7','8','9','10','11']),
            'start': {
                'dateTime': start_date.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_date.isoformat(),
                'timeZone': 'UTC',
            },
        }
        event = service.events().insert(calendarId=os.getenv('CALENDAR_ID'), body=event).execute()
    
        return f"Event created: {event.get('htmlLink')}"    
    
def get_st_en_date(date_str):
   date_range = date_str.split(" to ")
   return date_range[0],date_range[1]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        leave_days = request.form['leave_days']
        leave_period= request.form['leave_period']
        reason = request.form['reason']

        conn=get_db()
        conn.execute("INSERT INTO leave_applications (name, email, leave_days, leave_period, reason) VALUES (?, ?, ?, ?, ?)", (name, email, leave_days, leave_period, reason))
        conn.commit()
        conn.close()
        
        context={
             "name": name,
             "email": email,
             "leave_days":leave_days,
             "leave_period": leave_period,
             "reason":reason,
             }             
        message = Message(
        subject='New Leave Request Recieved | FlaskyLMS',
        recipients=recipients,
        html=render_template(template_name_or_list="leave_notification.html", **context))
        send_email(message)
        return render_template('thankyou.html')

    return render_template('lform.html')
    
@app.route('/leave_applications')
def leave_applications():  
    if 'user' not in session:
        return redirect(url_for('login'))
    c = get_db().cursor()
    c.execute("SELECT * FROM leave_applications")
    data = c.fetchall()
    c.close()

    return render_template('application_table.html', data=[row[1:] for row in data])
    
@app.route('/login', methods=['GET', 'POST'])
def login():

    error_message = ''
    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']
        
        c = get_db().cursor()
        c.execute("SELECT * FROM users WHERE email = ? AND password = ?",(username,password))
        data = c.fetchall()
        c.close()
        # Check if the credentials are valid
        if data:
            # Store the user ID in a session variable
            session['user'] = username
            
            return redirect(url_for('leave_applications'))
        else:
            error_message = 'Invalid username or password'

    # Render the login page with an error message if not present
    return render_template('login.html', error_message=error_message)
    
@app.route('/logout')
def logout():
    # Remove the session variables
    session.pop('user', None)
    session.pop('is_authenticated', None)
    
    return redirect(url_for('login'))
        
@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.get("data")
    data = json.loads(data)
    for item in data:
        email = item["email"]
        status = item["status"]
        db_status = get_status(email)
        print("db status for ", email, " is ", db_status)
        if db_status not in ['approved','rejected']:
            update_status(email, status)
            data=get_leave_rec(email)
            context={
             "name": data[1],
             "leave_period":data[4],
              "status": data[6],
              }
            message = Message(
            subject='Your Leave Request Status | FlaskyLMS',
            recipients=[email],
            html=render_template(template_name_or_list="emp_leave_notification.html", **context))
            send_email(message)
            
            #Create Event in Calendar
            if data[6] == 'approved':
               start_date,end_date = get_st_en_date(data[4])
               thr = threading.Thread(target = create_event, args = [data[1], start_date, end_date, data[5], service])
               thr.start()
        else:
            print("nothing to send")           
    return "submitted"
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
