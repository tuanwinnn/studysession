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

 #This is the page that displays study sessions, only viewable if user is logged in other wise prompts to log in
@main_bp.route('/sessions')
@login_required
def view_session():
    #Sessions user has joined
    joined = StudySession.query.filter(StudySession.members.any(id=current_user.id)).all()
    #All available sessions
    available = StudySession.query.filter(~StudySession.members.any(id=current_user.id)).all()

    return render_template('main/sessions.html', joined_sessions = joined, available_sessions = available)

#Leave session -- WORK IN PROGRESS
@main_bp.route('/leave_session')
def leave_session():
    return render_template('main/leave_session.html') #not created yet

#Join session -- WORK IN PROGRESS
@main_bp.route('/join_session')
def join_session():
    return render_template('main/join_session.html') #not created yet

#Create session -- WORK IN PROGRESS
@main_bp.route('/create_session')
def create_session():
    return render_template('main/create_session.html') #not created yet

#Edit session, but be "owner/creator" of session -- WORK IN PROGRESS
@main_bp.route('/edit_session')
def edit_session():
    return render_template('main/edit_session.html') #not created yet