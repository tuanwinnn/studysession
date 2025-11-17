# Studysession

A course-integrated study session coordination platform where students can create and join study sessions with classmates.

Google Doc: https://docs.google.com/document/d/1iHBsqym4T0VoHqEuDuFzItrlC4IJMhldQqj5BU9CPhY/edit?usp=sharing 

## Setup and Installation

1. Clone the repository:
```bash
git clone <https://github.com/tuanwinnn/studysession.git>
cd studysession
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate.bat
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python run.py
```

Or using Flask CLI:
```bash
flask run
```

5. Open your browser and navigate to `http://127.0.0.1:5000`

## Project Structure

```
studysession/
├── app/
│   ├── __init__.py          # App factory pattern for flexible configuration
│   ├── config.py            # Centralized configuration (SQLite URI, secrets)
│   ├── models.py            # SQLAlchemy models (User, StudySession)
│   ├── forms.py             # WTForms for input validation
│   ├── auth/                # Authentication blueprint (separation of concerns)
│   │   ├── routes.py        # Login routes
│   │   └── templates/auth/  # Auth-specific templates
│   ├── main/                # Main application blueprint
│   │   ├── routes.py        # Core page routes
│   │   └── templates/main/  # Main templates
│   ├── templates/           # Shared templates
│   │   └── base.html        # Base template with nav and flash messages
│   └── static/              # Static assets
│       └── styles.css       # Application styling
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
└── README.md
```

### Structure Rationale

- **App Factory Pattern**: `create_app()` allows for flexible configuration and easier testing
- **Blueprints**: Separate auth and main concerns for maintainable, modular code
- **Template Inheritance**: Base template ensures consistent layout across all pages
- **SQLAlchemy + SQLite**: Simple persistence layer that scales to PostgreSQL later
- **Flask-Login**: Authentication infrastructure ready for M2/M3 implementation
- **WTForms**: Server-side validation with CSRF protection built-in

## Available Routes

- `/` - Home page
- `/feature` - Study sessions listing (demo page)
- `/auth/login` - Login form (validates but returns "Not implemented")

## Screenshot

![Home Page](homePage.png)

![Login Page](loginPage.png)

![Study Sessions Page](studySessions.png)

## Team Roles

- Tuan Nguyen - Developer
- Carlie Yem - Developer
- Jongha Kim - Developer

## Tech Stack

- Flask 3.0 - Web framework
- SQLAlchemy - ORM for database operations
- Flask-Login - User session management
- WTForms - Form handling and validation
- SQLite - Development database

## Next Steps (M2/M3)

- Implement actual user authentication
- Add CRUD operations for study sessions
- Course enrollment verification
- Session filtering and search
- Real-time participant updates
