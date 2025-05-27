from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, PasswordField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from hospital.models import User, Patient

class ExistingPatientRegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password1 = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password1')])
    submit = SubmitField('Create Account')


class NewPatientRegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password1 = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password1')])
    submit = SubmitField('Create Account')

    def validate_email(self, email):
        if Patient.query.filter_by(email=email.data).first():
            raise ValidationError("Patient with this email already exists.")
        

class Login_form(FlaskForm):
    email = StringField(label='Enter email:', validators=[DataRequired()])
    password = PasswordField(label='Enter password:', validators=[DataRequired()])
    submit = SubmitField(label='LOGIN')


class PurchaseForm(FlaskForm):
    submit = SubmitField("Kup")
