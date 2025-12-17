from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, BooleanField, DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from datetime import datetime
from app.models import User

# Login form for existing users
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])  # required, must be a valid email
    password = PasswordField('Password', validators=[DataRequired()])   # required password field
    submit = SubmitField('Log In')

# Registration form for new users
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')


class SessionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    date = DateTimeField(
        'Date',
        format="%Y-%m-%d %H:%M",
        validators=[DataRequired()],
    )
    location = StringField('Location', validators=[DataRequired(), Length(max=200)])
    topic = TextAreaField('Topic')  # optional

    submit = SubmitField('Create Session')

    def validate_date(self, field):
        # must be in the future
        if field.data is not None and field.data <= datetime.utcnow():
            raise ValidationError("Date must be in the future.")

# Form for creating/editing a study session
class StudySessionForm(FlaskForm):
    title = StringField('Session Title', validators=[DataRequired(), Length(max=200)])  # required session title
    date = StringField('Date (YYYY-MM-DD)', validators=[DataRequired()])               # simple date input as string
    time = StringField('Time (e.g., 3:00 PM - 5:00 PM)', validators=[DataRequired(), Length(max=20)])  # time range text
    location = StringField('Location', validators=[DataRequired(), Length(max=200)])   # where the session takes place
    topic = StringField('Topic (Optional)', validators=[Length(max=100)])              # optional topic/subject
    #Recurring session fields
    is_recurring = BooleanField('Repeat Session')
    recurrence_interval = SelectField(
        'Recurrence Interval', 
        choices=[('weekly', 'Weekly'), ('biweekly', 'Biweekly'), ('monthly', 'Monthly')])
    
    submit = SubmitField('Create Session')

class SessionCommentForm(FlaskForm):
    content = TextAreaField(
        'Add a comment', 
        validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Post Comment')