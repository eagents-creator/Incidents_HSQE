from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from .translations import get_text
import os

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    
    # Configure app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-please-change')
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'hsqe.db'))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    print(f"\nInitializing Flask app...")
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"Database path: {db_path}")
    
    # Set environment-specific settings
    if os.environ.get('FLASK_ENV') == 'production':
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['REMEMBER_COOKIE_SECURE'] = True
    else:
        app.config['DEBUG'] = True
        app.config['TESTING'] = True

    # Initialize extensions
    print("Initializing extensions...")
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    csrf.init_app(app)
    app.config['WTF_CSRF_TIME_LIMIT'] = None
    app.config['WTF_CSRF_ENABLED'] = True
    api = Api(app)
    
    # Import models and blueprints
    from app.models import User
    from app.auth import auth as auth_blueprint
    from app.main import main as main_blueprint
    from app.api import api_bp

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Add get_text function to template context
    app.jinja_env.globals.update(get_text=get_text)

    # Register blueprints
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_bp, url_prefix='/api')

    # Create database tables
    with app.app_context():
        if not os.path.exists(db_path):
            print(f"Creating database at {db_path}")
            db.create_all()
            print("Database tables created successfully")
        else:
            print(f"Database exists at {db_path}")
            print(f"File size: {os.path.getsize(db_path)} bytes")
            print(f"File permissions: {oct(os.stat(db_path).st_mode)[-3:]}")

    return app
