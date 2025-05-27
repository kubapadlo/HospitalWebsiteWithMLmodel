from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:toor@localhost/hospital'
app.config['SECRET_KEY'] = '7f2a716d0e93c4dc292e1cd1'    

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)   
login_manager.login_view = 'login_page'
login_manager.login_message_category = 'info'

from hospital import routes