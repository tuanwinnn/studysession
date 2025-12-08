from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import StudySession

main_bp = Blueprint('main', __name__, template_folder='templates')

@main_bp.route('/')
def index():
    return render_template('main/index.html')

@main_bp.route('/feature')
def feature():
    return render_template('main/feature.html')

