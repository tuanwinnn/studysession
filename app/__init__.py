from flask import Flask
from flask_login import LoginManager
from .config import Config
from .models import db, User

# Set up login manager for handling user sessions
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # redirect here if not logged in
login_manager.login_message = "Please log in to access this page."

def create_app():
    # Application factory
    app = Flask(__name__)
    app.config.from_object(Config)  # load config settings
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    
    # Callback to load a user from the session
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints for auth and main views
    from .auth.routes import auth_bp
    from .main.routes import main_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    return app
