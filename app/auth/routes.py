from flask import Blueprint, render_template, flash, redirect, url_for
from ..forms import LoginForm


auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # User logs in and redirects to view their sessions
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user) # <-- Logs user in
            # -- Success message for logging in could be placed here -- #
            return redirect(url_for('main.view_session'))
        

    # Renders if the login validation fails
    return render_template('auth/login.html', form=form)
