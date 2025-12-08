from flask import Flask
from flask_login import LoginManager
from .config import Config
from .models import db, User

login_manager = LoginManager()
login_manager.LoginView = 'auth.login'
login_manager.LoginMessage = "Please log in to access this page."

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from .auth.routes import auth_bp
    from .main.routes import main_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)

    
    return app
