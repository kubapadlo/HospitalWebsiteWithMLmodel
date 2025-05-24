from hospital import app #, conn
from hospital.models import User, Patient, Doctor, Appointment, Visit, HeartData, MLPrediction, Drug, Order
from hospital import db

from hospital import app
from flask import render_template

@app.route('/home')
@app.route('/')
def home_page():
    return render_template('home.html')