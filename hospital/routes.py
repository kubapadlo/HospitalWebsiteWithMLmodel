from hospital import app #, conn
from hospital.models import User, Patient, Doctor, Appointment, Visit, HeartData, MLPrediction, Drug, Order
from hospital.forms import ExistingPatientRegisterForm, NewPatientRegisterForm, Login_form
from hospital import db

from hospital import app
from flask import render_template, url_for, flash, request, redirect, abort
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps

@app.route('/home')
@app.route('/')
def home_page():
    return render_template('home.html')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function


@app.route('/doctors')
def doctor_page():
    doctors = Doctor.query.all()
    return render_template('doctors.html', doctors=doctors)

@app.route('/login', methods=['GET', 'POST']) 
def login_page():
    form = Login_form()

    if form.validate_on_submit():
        attempted_user = User.query.join(User.patient).filter(Patient.email == form.email.data).first()

        if attempted_user and attempted_user.is_password_correct(form.password.data):
            login_user(attempted_user)
            flash(f"Logged in as {attempted_user.role}: {attempted_user.userID}", category='success')
            return redirect(url_for('doctor_page') if attempted_user.role == 'admin' else url_for('home_page'))
        else:
            flash('Wrong email or password', category='danger')
        
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form_type = request.args.get('type')  # 'existing' lub 'new'

    if form_type == 'existing':
        form = ExistingPatientRegisterForm()
    elif form_type == 'new':
        form = NewPatientRegisterForm()
    else:
        return render_template("register_choice.html")

    if form.validate_on_submit():
        if form_type == 'existing':
            existing_patient = Patient.query.filter_by(email=form.email.data).first()

            if existing_patient:
                if existing_patient.user:
                    flash("Account already exists for this patient.", category='danger')
                    return redirect(url_for('register_page', type='existing'))

                user_to_create = User(
                    patient_id=existing_patient.patientID,
                    password=form.password1.data
                )
                db.session.add(user_to_create)
                db.session.commit()
                login_user(user_to_create)
                flash("Account created.", category='success')
                return redirect(url_for('home_page'))

            flash("No patient found with that email.", category='danger')

        elif form_type == 'new':
            new_patient = Patient(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                birth_date=form.date_of_birth.data,
                adress=form.address.data,
                email=form.email.data
            )
            db.session.add(new_patient)
            db.session.flush()

            user_to_create = User(
                patient_id=new_patient.patientID,
                password=form.password1.data
            )
            db.session.add(user_to_create)
            db.session.commit()
            login_user(user_to_create)
            flash("Account created and patient registered.", category='success')
            return redirect(url_for('home_page'))

    return render_template("register_form.html", form=form, type=form_type)


@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been log out', category='info')
    return redirect(url_for('home_page'))