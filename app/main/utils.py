# app/main/util.py
from app.models import StudySession

def suggest_location(session):
    """
    Suggests a location based on the number of participants.
    """
    participant_count = session.get_participant_count()

    if participant_count <= 3:
        return "Library Group Study Room"
    elif participant_count <= 6:
        return "Student Union Tables"
    else:
        return "Book Private Library Room"