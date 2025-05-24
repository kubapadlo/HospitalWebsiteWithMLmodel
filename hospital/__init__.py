from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:toor@localhost/hospital'
app.config['SECRET_KEY'] = '7f2a716d0e93c4dc292e1cd1'    

db = SQLAlchemy(app)

from hospital import routes