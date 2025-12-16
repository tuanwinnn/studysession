from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import StudySession, SessionComment, db
from app.forms import StudySessionForm, SessionCommentForm
from app.main.utils import suggest_location
from datetime import datetime

# Main blueprint for core app views
main_bp = Blueprint('main', __name__, template_folder='templates')

@main_bp.route('/')
def index():
    # Landing page
    return render_template('main/index.html')

@main_bp.route('/feature')
def feature():
    # Simple feature/info page
    return render_template('main/feature.html')

# READ: View all sessions
@main_bp.route('/sessions')
@login_required
def view_sessions():
    # Sessions the current user has already joined
    joined = StudySession.query.filter(StudySession.members.any(id=current_user.id)).all()
    # Sessions user has not joined yet
    available = StudySession.query.filter(~StudySession.members.any(id=current_user.id)).all()

    return render_template('main/sessions.html', joined_sessions=joined, available_sessions=available)

# CREATE: Create a new session
@main_bp.route('/create_session', methods=['GET', 'POST'])
@login_required
def create_session():
    form = StudySessionForm()
    if form.validate_on_submit():
        try:
            # Convert date string from form to datetime object
            session_date = datetime.strptime(form.date.data, '%Y-%m-%d')
            
            # Create new StudySession instance
            session = StudySession(
                title=form.title.data,
                date=session_date,
                time=form.time.data,
                location=form.location.data,
                topic=form.topic.data or '',
                creator_id=current_user.id
            )
            
            # Creator automatically becomes a member
            session.members.append(current_user)
            
            db.session.add(session)
            db.session.commit()

            #Create recurring sessions if applicable
            if session.is_recurring:
                create_recurring_sessions(session)
                db.session.commit()
            
            flash('Study session created successfully!', 'success')
            return redirect(url_for('main.view_sessions'))
        except ValueError:
            # Invalid date format
            flash('Invalid date format. Please use YYYY-MM-DD', 'error')
    
    return render_template('main/create_session.html', form=form)
# CREATE: recurring sessions helper
def create_recurring_sessions(parent_session, count = 4):
    delta = datetime(
        weeks=1 if parent_session.recurrence_interval == 'weekly' else 2)
    
    for i in range(1, count + 1):
        new_session = StudySession(
            title=parent_session.title,
            date=parent_session.date + (i * delta),
            time=parent_session.time,
            location=parent_session.location,
            topic=parent_session.topic or '',
            creator_id=parent_session.creator_id,
            parent_id=parent_session.id,
        )
        db.session.add(new_session)
    

# UPDATE: Edit a session
@main_bp.route('/edit_session/<int:session_id>', methods=['GET', 'POST'])
@login_required
def edit_session(session_id):
    session = StudySession.query.get_or_404(session_id)
    
    # Only the session creator can edit it
    if session.creator_id != current_user.id:
        flash('You can only edit sessions you created.', 'error')
        return redirect(url_for('main.view_sessions'))
    
    form = StudySessionForm()
    
    if form.validate_on_submit():
        try:
            # Update session fields from form data
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
    
    # Pre-fill the form with existing session data on GET
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
    
    # Only the creator can delete the session
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
    
    # Don’t allow joining past sessions
    if session.is_past():
        flash('Cannot join a session that has already occurred.', 'error')
        return redirect(url_for('main.view_sessions'))
    
    # Prevent duplicate joins
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
    
    # Must be a member to leave
    if current_user not in session.members.all():
        flash('You are not a member of this session.', 'error')
        return redirect(url_for('main.view_sessions'))
    
    # Creator cannot leave (they should delete instead)
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
    is_member = current_user in session.members.all()  # whether current user has joined
    is_creator = session.creator_id == current_user.id  # whether current user created it
    comment_form = SessionCommentForm()
    return render_template(
        'main/session_detail.html',
        session=session,
        is_member=is_member,
        is_creator=is_creator,
        comment_form=comment_form
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
            author_id=current_user.id,
            session_id=session.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Comment added successfully!', 'success')
    
    return redirect(url_for('main.session_detail', session_id=session.id))

# LOCATION SUGGESTION: Suggest a location based on topic
@main_bp.route('/sessions/<int:session_id>/suggest_location')
@login_required
def suggest_session_location(session_id):
    session = StudySession.query.get_or_404(session_id)
    suggestion = suggest_location(session)

    flash(f'Suggested location: {suggestion}', 'info')
    return redirect(url_for('main.view_sessions', session_id=session.id))