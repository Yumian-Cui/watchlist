from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, DateField, PasswordField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from flask_login import current_user
from wtforms import StringField as BaseStringField, PasswordField as BasePasswordField, Field as BaseField

from app.models import User

class Field(BaseField):
    def __init__(self, label=None, validators=None, **kwargs):
        kwargs.setdefault('render_kw', {}).setdefault('class', 'form-field')
        super().__init__(label, validators, **kwargs)

class AuthStringField(Field, BaseStringField):
    pass

class AuthPasswordField(Field, BasePasswordField):
    pass


class SettingsForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=20)])
    username = StringField('Username', validators=[DataRequired(), Length(max=20)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=50)])
    submit = SubmitField('Update')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user and user.id != current_user.id:
            raise ValidationError('Username already exists.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and user.id != current_user.id:
            raise ValidationError('Email already exists.')

#Create a new class that inherits from FlaskForm:
class MovieForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=60)]) #first argument is the label of the field, which is used to generate the label tag in the HTML form
    year = StringField('Year', validators=[DataRequired(), Length(min=4, max=4, message='Invalid year.')]) #length must be 4
    # year = DateField('year', validators=[DataRequired()], format='%Y')
    submit = SubmitField()


# Authentification form fields follow a different styling than MovieForm
class LoginForm(FlaskForm):
    identifier = AuthStringField('Username or Email', validators=[DataRequired()])
    password = AuthPasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegisterForm(FlaskForm):
    username = AuthStringField('Username', validators=[DataRequired()])
    email = AuthStringField('Email', validators=[DataRequired(), Email()])
    password = AuthPasswordField('Password', validators=[DataRequired()])
    create = SubmitField('Create')

class ResetPasswordForm(FlaskForm):
    new_password = AuthPasswordField('New Password', validators=[DataRequired()])
    confirm_password = AuthPasswordField('Confirm Password', validators=[DataRequired()])
    reset = SubmitField('Reset')