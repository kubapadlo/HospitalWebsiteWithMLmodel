from hospital import app #, conn
from hospital.models import User, Patient, Doctor, Appointment, Visit, HeartData, MLPrediction, Drug, Order
from hospital.forms import ExistingPatientRegisterForm, NewPatientRegisterForm, Login_form, PurchaseForm
from hospital import db

from hospital import app
from flask import render_template, url_for, flash, request, redirect, abort
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps

@app.route('/home')
@app.route('/')
def home_page():
    return render_template('home.html')

def doctor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'doctor':
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
        email_input = form.email.data
        password_input = form.password.data

        # Próbujemy znaleźć użytkownika jako pacjenta
        attempted_user = User.query.join(User.patient).filter(Patient.email == email_input).first()

        # Jeśli nie znaleziono pacjenta, szukamy lekarza
        if not attempted_user:
            attempted_user = User.query.join(User.doctor).filter(Doctor.email == email_input).first()

        # Jeśli użytkownik istnieje i hasło się zgadza
        if attempted_user and attempted_user.is_password_correct(password_input):
            login_user(attempted_user)

            flash(f"Zalogowano!", category='success')

            # Przekierowanie w zależności od roli
            if attempted_user.role == 'doctor':
                return redirect(url_for('doctor_profile'))
            elif attempted_user.role == 'admin':
                return redirect(url_for('admin_page'))
            else:
                return redirect(url_for('home_page'))

        flash('Nieprawidłowy email lub hasło', category='danger')

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
                    flash("Konto z takim emailem już istnieje", category='danger')
                    return redirect(url_for('register_page', type='existing'))

                user_to_create = User(
                    patient_id=existing_patient.patientID,
                    password=form.password1.data
                )
                db.session.add(user_to_create)
                db.session.commit()
                login_user(user_to_create)
                flash("Konto utworzone!", category='success')
                return redirect(url_for('home_page'))

            flash("Nie ma konta przypisanego do tego emaila", category='danger')

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
            flash("Konto utworzone!", category='success')
            return redirect(url_for('home_page'))

    return render_template("register_form.html", form=form, type=form_type)


@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been log out', category='info')
    return redirect(url_for('home_page'))


@app.route('/market', methods=['GET', 'POST'])
def market_page():
    drugs = Drug.query.all()
    form = PurchaseForm()

    if request.method == 'POST' and current_user.is_authenticated:
        drug_name = request.form.get('purchased_item').strip()
        drug = Drug.query.filter_by(drug_name=drug_name).first()
        if drug:
            order = Order(userID=current_user.userID, drugID=drug.drugID)
            db.session.add(order)
            db.session.commit()
            flash(f"Kupiłeś {drug.drug_name}!", "success")
            return redirect(url_for('market_page'))

    return render_template('market.html', drugs=drugs, purchase_form=form)

@app.route('/profile')
@login_required
def profile_page():
    orders = Order.query.filter_by(userID=current_user.userID).all()
    appointments = Appointment.query.filter_by(patientID=current_user.patient_id).all()

    return render_template('profile.html', orders=orders, appointments=appointments)

@app.route('/doctors')
def doctors_page():
    doctors = Doctor.query.all()
    return render_template('doctors.html', doctors=doctors)


@app.route('/book/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def book_appointment(doctor_id):
    # Przykładowe umawianie na jutro
    from datetime import date, timedelta
    tomorrow = date.today() + timedelta(days=1)

    appointment = Appointment(patientID=current_user.patient_id, doctorID=doctor_id, date=tomorrow, status="Zaplanowana")
    db.session.add(appointment)
    db.session.commit()
    flash("Wizyta została umówiona!", "success")
    return redirect(url_for('doctors_page'))


@app.route('/doctor/profile', methods=['GET', 'POST'])
@login_required
def doctor_profile():
    # Pobierz wszystkie wizyty przypisane do danego lekarza
    doctor_id = current_user.doctorID  # Zakładamy, że jest powiązanie User ↔ Doctor
    appointments = Appointment.query.filter_by(doctorID=doctor_id).all()

    if request.method == 'POST':
        appointment_id = request.form.get('appointment_id')
        status = request.form.get('status')
        diagnosis = request.form.get('diagnosis')
        notes = request.form.get('notes')

        # Zmień status wizyty
        appointment = Appointment.query.get(appointment_id)
        if appointment:
            appointment.status = status

            # Dodaj lub zaktualizuj Visit
            visit = Visit.query.filter_by(appointmentID=appointment_id).first()
            if not visit:
                visit = Visit(appointmentID=appointment_id)
                db.session.add(visit)
            visit.dignosis = diagnosis
            visit.notes = notes

            db.session.commit()
            flash('Wizyta została zaktualizowana.', 'success')
        return redirect(url_for('doctor_profile'))

    return render_template('doctor_profile.html', appointments=appointments)


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_page():
    patients = Patient.query.all()
    doctors = Doctor.query.all()
    appointments = Appointment.query.all()
    return render_template('admin.html', patients=patients, doctors=doctors, appointments=appointments)