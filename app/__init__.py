from flask import Flask, redirect, url_for, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_required
from markupsafe import Markup
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret-key'
    heroku config:set DATABASE_URL="mysql+mysqlconnector://root:12345@localhost/mydb"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @app.template_filter()
    def nl2br(value):
        result = '<br>'.join(value.splitlines())
        return Markup(result)

    # Register the filter with the app
    app.jinja_env.filters['nl2br'] = nl2br

    @login_manager.user_loader
    def load_user(user_id):
        from .models import Users
        return Users.query.get(int(user_id))

    with app.app_context():
        # Import parts of our application
        from .models import Users, WorkoutNote, Folder
        from .auth import auth as auth_blueprint
        app.register_blueprint(auth_blueprint)
        
        # Create database tables
        db.create_all()

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .workout import workout as workout_blueprint
    app.register_blueprint(workout_blueprint)

    @app.route('/create_folder', methods=['POST'])
    @login_required
    def create_folder():
        folder_name = request.form.get('folder_name')
        if folder_name:
            new_folder = Folder(name=folder_name, user_id=current_user.id)
            db.session.add(new_folder)
            db.session.commit()
        return redirect(url_for('workout.notes'))

    @app.route('/delete_note/<int:note_id>', methods=['POST'])
    def delete_note(note_id):
        try:
            note = WorkoutNote.query.get(note_id)
            if note:
                db.session.delete(note)
                db.session.commit()
                return redirect(url_for('workout.notes'))
            else:
                return "Note not found", 404
        except Exception as e:
            return str(e), 500

    @app.before_request
    def before_request():
        if not current_user.is_authenticated and request.endpoint not in ['auth.login', 'auth.signup', 'static']:
            return redirect(url_for('auth.login'))

    app.debug = True

    return app