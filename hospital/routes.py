from hospital import app
from flask import render_template

@app.route('/home')
@app.route('/')
def home_page():
    return render_template('home.html')