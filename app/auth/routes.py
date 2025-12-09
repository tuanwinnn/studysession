from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_user, logout_user, current_user
from app.forms import LoginForm, RegistrationForm
from app.models import User, db

# Auth blueprint for login/register/logout routes
auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, skip login page
    if current_user.is_authenticated:
        return redirect(url_for('main.view_sessions'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Look up user by email
        user = User.query.filter_by(email=form.email.data).first()

        # Check password and log in if valid
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Successfully logged in!', 'success')
            return redirect(url_for('main.view_sessions'))
        else:
            flash('Invalid email or password', 'error')

    # Render login form (GET or failed POST)
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Already logged in users don’t need to register
    if current_user.is_authenticated:
        return redirect(url_for('main.view_sessions'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create new user with hashed password
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    # Render registration form
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
def logout():
    # Log out current user and redirect to home
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
