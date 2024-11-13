from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
# Enable debug mode
app.debug = True
app.config['SECRET_KEY'] = 'dev-key-123'  # Simple key for development
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    tech_stack = db.Column(db.String(200))
    project_url = db.Column(db.String(200))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    try:
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        projects = Project.query.order_by(Project.created_date.desc()).all()
        return render_template('index.html', projects=projects)
    except Exception as e:
        print(f"Error in index route: {str(e)}")
        return str(e), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()

            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                return redirect(url_for('index'))
            flash('Invalid username or password')
        return render_template('login.html')
    except Exception as e:
        print(f"Error in login route: {str(e)}")
        return str(e), 500


@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')

            if User.query.filter_by(username=username).first():
                flash('Username already exists')
                return redirect(url_for('register'))

            user = User(username=username,
                        email=email,
                        password_hash=generate_password_hash(password),
                        is_admin=False)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        return render_template('register.html')
    except Exception as e:
        print(f"Error in register route: {str(e)}")
        return str(e), 500


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/admin')
@login_required
def admin():
    try:
        if not current_user.is_admin:
            return redirect(url_for('index'))
        projects = Project.query.all()
        users = User.query.all()
        return render_template('admin.html', projects=projects, users=users)
    except Exception as e:
        print(f"Error in admin route: {str(e)}")
        return str(e), 500


@app.route('/admin/project/add', methods=['GET', 'POST'])
@login_required
def add_project():
    try:
        if not current_user.is_admin:
            return redirect(url_for('index'))

        if request.method == 'POST':
            project = Project(title=request.form.get('title'),
                              description=request.form.get('description'),
                              image_url=request.form.get('image_url'),
                              tech_stack=request.form.get('tech_stack'),
                              project_url=request.form.get('project_url'))
            db.session.add(project)
            db.session.commit()
            return redirect(url_for('admin'))
        return render_template('add_project.html')
    except Exception as e:
        print(f"Error in add_project route: {str(e)}")
        return str(e), 500


def init_db():
    try:
        with app.app_context():
            # Create all tables
            db.create_all()

            # Check if admin user exists
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin = User(username='admin',
                             email='admin@example.com',
                             password_hash=generate_password_hash('admin123'),
                             is_admin=True)
                db.session.add(admin)
                db.session.commit()
                print("Admin user created successfully")
            else:
                print("Admin user already exists")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise e


if __name__ == '__main__':
    print("Initializing database...")
    init_db()
    print("Starting application...")
    app.run(host='0.0.0.0', port=8080)
