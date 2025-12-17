from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import StudySession, SessionComment, db
from app.forms import StudySessionForm, SessionCommentForm
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__, template_folder='templates')

@main_bp.route('/')
def index():
    return render_template('main/index.html')

@main_bp.route('/feature')
def feature():
    return render_template('main/feature.html')

# READ: View all sessions
@main_bp.route('/sessions')
@login_required
def view_sessions():
    joined = StudySession.query.filter(StudySession.members.any(id=current_user.id)).all()
    available = StudySession.query.filter(~StudySession.members.any(id=current_user.id)).all()
    return render_template('main/sessions.html', joined_sessions=joined, available_sessions=available)

# CREATE: Create a new session
@main_bp.route('/create_session', methods=['GET', 'POST'])
@login_required
def create_session():
    form = StudySessionForm()
    if form.validate_on_submit():
        try:
            session_date = datetime.strptime(form.date.data, '%Y-%m-%d')
            
            session = StudySession(
                title=form.title.data,
                date=session_date,
                time=form.time.data,
                location=form.location.data,
                topic=form.topic.data or '',
                creator_id=current_user.id,
                is_recurring=form.is_recurring.data,
                recurrence_interval=form.recurrence_interval.data if form.is_recurring.data else None
            )
            
            session.members.append(current_user)
            db.session.add(session)
            db.session.commit()

            # Create recurring sessions if applicable
            if session.is_recurring:
                create_recurring_sessions(session)
                db.session.commit()
            
            flash('Study session created successfully!', 'success')
            return redirect(url_for('main.view_sessions'))
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD', 'error')
    
    return render_template('main/create_session.html', form=form)

# Helper function for recurring sessions
def create_recurring_sessions(parent_session, count=4):
    """Create recurring child sessions based on the parent session"""
    if parent_session.recurrence_interval == 'weekly':
        delta = timedelta(weeks=1)
    elif parent_session.recurrence_interval == 'biweekly':
        delta = timedelta(weeks=2)
    elif parent_session.recurrence_interval == 'monthly':
        delta = timedelta(days=30)  # Approximate month
    else:
        return  # No recurrence
    
    for i in range(1, count + 1):
        new_session = StudySession(
            title=parent_session.title,
            date=parent_session.date + (i * delta),
            time=parent_session.time,
            location=parent_session.location,
            topic=parent_session.topic or '',
            creator_id=parent_session.creator_id,
            parent_id=parent_session.id,
            is_recurring=False,  # Child sessions are not recurring themselves
            recurrence_interval=None
        )
        db.session.add(new_session)

# UPDATE: Edit a session
@main_bp.route('/edit_session/<int:session_id>', methods=['GET', 'POST'])
@login_required
def edit_session(session_id):
    session = StudySession.query.get_or_404(session_id)
    
    if session.creator_id != current_user.id:
        flash('You can only edit sessions you created.', 'error')
        return redirect(url_for('main.view_sessions'))
    
    form = StudySessionForm()
    
    if form.validate_on_submit():
        try:
            session.title = form.title.data
            session.date = datetime.strptime(form.date.data, '%Y-%m-%d')
            session.time = form.time.data
            session.location = form.location.data
            session.topic = form.topic.data or ''
            
            db.session.commit()
            flash('Session updated successfully!', 'success')
            return redirect(url_for('main.view_sessions'))
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD', 'error')
    
    if request.method == 'GET':
        form.title.data = session.title
        form.date.data = session.date.strftime('%Y-%m-%d')
        form.time.data = session.time
        form.location.data = session.location
        form.topic.data = session.topic
    
    return render_template('main/edit_session.html', form=form, session=session)

# DELETE: Delete a session
@main_bp.route('/delete_session/<int:session_id>', methods=['POST'])
@login_required
def delete_session(session_id):
    session = StudySession.query.get_or_404(session_id)
    
    if session.creator_id != current_user.id:
        flash('You can only delete sessions you created.', 'error')
        return redirect(url_for('main.view_sessions'))
    
    db.session.delete(session)
    db.session.commit()
    flash('Session deleted successfully!', 'success')
    return redirect(url_for('main.view_sessions'))

# JOIN: Join a session
@main_bp.route('/join_session/<int:session_id>', methods=['POST'])
@login_required
def join_session(session_id):
    session = StudySession.query.get_or_404(session_id)
    
    if session.is_past():
        flash('Cannot join a session that has already occurred.', 'error')
        return redirect(url_for('main.view_sessions'))
    
    if current_user in session.members.all():
        flash('You have already joined this session.', 'info')
        return redirect(url_for('main.view_sessions'))
    
    session.members.append(current_user)
    db.session.commit()
    flash('Successfully joined the session!', 'success')
    return redirect(url_for('main.view_sessions'))

# LEAVE: Leave a session
@main_bp.route('/leave_session/<int:session_id>', methods=['POST'])
@login_required
def leave_session(session_id):
    session = StudySession.query.get_or_404(session_id)
    
    if current_user not in session.members.all():
        flash('You are not a member of this session.', 'error')
        return redirect(url_for('main.view_sessions'))
    
    if session.creator_id == current_user.id:
        flash('You cannot leave a session you created. Delete it instead.', 'error')
        return redirect(url_for('main.view_sessions'))
    
    session.members.remove(current_user)
    db.session.commit()
    flash('You have left the session.', 'info')
    return redirect(url_for('main.view_sessions'))

# View session details page
@main_bp.route('/session/<int:session_id>')
@login_required
def session_detail(session_id):
    session = StudySession.query.get_or_404(session_id)
    is_member = current_user in session.members.all()
    is_creator = session.creator_id == current_user.id
    comment_form = SessionCommentForm()
    
    # Get location suggestion
    location_suggestion = suggest_location(session)
    
    return render_template(
        'main/session_detail.html',
        session=session,
        is_member=is_member,
        is_creator=is_creator,
        comment_form=comment_form,
        location_suggestion=location_suggestion
    )

# COMMENT: Add comment to session
@main_bp.route('/session/<int:session_id>/comment', methods=['POST'])
@login_required
def add_comment(session_id):
    session = StudySession.query.get_or_404(session_id)
    form = SessionCommentForm()
    
    if form.validate_on_submit():
        comment = SessionComment(
            content=form.content.data,
            user_id=current_user.id,
            session_id=session.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Comment added successfully!', 'success')
    
    return redirect(url_for('main.session_detail', session_id=session.id))

# Helper import
from app.main.utils import suggest_location