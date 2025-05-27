from hospital import db, bcrypt, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    userID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patientID'))
    doctorID = db.Column(db.Integer, db.ForeignKey('Doctors.doctorID'))
    password_hash = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(45), nullable=False, default='user')

    doctor = db.relationship('Doctor', backref='user', uselist=False)
    patient = db.relationship('Patient', back_populates='user', uselist=False)
    orders = db.relationship('Order', back_populates='user')

    def get_id(self):
        return str(self.userID)

    @property
    def password(self): # pseudo-pole TYLKO DO ODCZYTU
        raise AttributeError("Hasło nie może być odczytane!")
    
    @password.setter        # definiuje co sie dzieje gdy przypisuje wartosc do pola password(automatyczne hashowanie)
    def password(self, plain_password):
        self.password_hash = bcrypt.generate_password_hash(plain_password).decode('utf-8')

    def is_password_correct(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

class Patient(db.Model):
    __tablename__ = 'patients'
    patientID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    adress = db.Column(db.String(45), nullable=False)
    email = db.Column(db.String(100), unique=True)

    user = db.relationship('User', back_populates='patient')
    appointments = db.relationship('Appointment', back_populates='patient')


class Doctor(db.Model):
    __tablename__ = 'Doctors'
    doctorID = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    degree = db.Column(db.String(45), nullable=False)
    specialization = db.Column(db.String(45), nullable=False)
    email = db.Column(db.String(100), unique=True)

    appointments = db.relationship('Appointment', back_populates='doctor')


class Appointment(db.Model):
    __tablename__ = 'Apointments'
    apointmentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patientID = db.Column(db.Integer, db.ForeignKey('patients.patientID'), nullable=False)
    doctorID = db.Column(db.Integer, db.ForeignKey('Doctors.doctorID'), nullable=False)
    date = db.Column(db.Date)
    status = db.Column(db.String(45))

    patient = db.relationship('Patient', back_populates='appointments')
    doctor = db.relationship('Doctor', back_populates='appointments')
    visits = db.relationship('Visit', back_populates='appointment')


class Visit(db.Model):
    __tablename__ = 'Vistis'
    visitID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    appointmentID = db.Column(db.Integer, db.ForeignKey('Apointments.apointmentID'), nullable=False)
    notes = db.Column(db.String(45))
    dignosis = db.Column(db.String(45))

    appointment = db.relationship('Appointment', back_populates='visits')
    heart_data = db.relationship('HeartData', back_populates='visit')


class HeartData(db.Model):
    __tablename__ = 'heart_data'
    heartID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    visitID = db.Column(db.Integer, db.ForeignKey('Vistis.visitID'), nullable=False)
    chest_width = db.Column(db.Integer)
    heart_width = db.Column(db.Integer)
    heart_area = db.Column(db.Integer)
    inscribed_circle_area = db.Column(db.Integer)
    heart_tip_inscribed_circle_radius = db.Column(db.Integer)

    visit = db.relationship('Visit', back_populates='heart_data')
    prediction = db.relationship('MLPrediction', back_populates='heart_data', uselist=False)


class MLPrediction(db.Model):
    __tablename__ = 'MLprediction'
    MLpredictionID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    heartdataID = db.Column(db.Integer, db.ForeignKey('heart_data.heartID'), nullable=False)
    prediction = db.Column(db.Integer)

    heart_data = db.relationship('HeartData', back_populates='prediction')


class Drug(db.Model):
    __tablename__ = 'drugs'
    drugID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    drug_name = db.Column(db.String(45), nullable=False)
    prize = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255), nullable=False)

    orders = db.relationship('Order', back_populates='drug') 


class Order(db.Model):
    __tablename__ = 'orders'
    orderID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userID = db.Column(db.Integer, db.ForeignKey('users.userID'))
    drugID = db.Column(db.Integer, db.ForeignKey('drugs.drugID'))

    user = db.relationship('User', back_populates='orders')
    drug = db.relationship('Drug', back_populates='orders')

