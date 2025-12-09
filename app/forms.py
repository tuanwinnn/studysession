from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.models import User

# Login form for existing users
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])  # required, must be a valid email
    password = PasswordField('Password', validators=[DataRequired()])   # required password field
    submit = SubmitField('Log In')

# Registration form for new users
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])  # username length constraints
    email = StringField('Email', validators=[DataRequired(), Email()])                      # required, valid email
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])        # minimum password length
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])  # must match password
    submit = SubmitField('Register')
    
    # Custom validator: ensure username is unique
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    # Custom validator: ensure email is unique
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

# Form for creating/editing a study session
class StudySessionForm(FlaskForm):
    title = StringField('Session Title', validators=[DataRequired(), Length(max=200)])  # required session title
    date = StringField('Date (YYYY-MM-DD)', validators=[DataRequired()])               # simple date input as string
    time = StringField('Time (e.g., 3:00 PM - 5:00 PM)', validators=[DataRequired(), Length(max=20)])  # time range text
    location = StringField('Location', validators=[DataRequired(), Length(max=200)])   # where the session takes place
    topic = StringField('Topic (Optional)', validators=[Length(max=100)])              # optional topic/subject
    submit = SubmitField('Create Session')
