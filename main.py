import sys
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy
import flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, Book, User
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

print("Python version:", sys.version)
print("SQLAlchemy version:", sqlalchemy.__version__)
print("Flask-SQLAlchemy version:", flask_sqlalchemy.__version__)

print("Imports completed")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///books.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Initialize the database with the app
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

print("Flask app created")

# Create tables within app context
with app.app_context():
    db.create_all()

print("Database initialized")

@app.route('/')
@login_required
def home():
    books = db.session.query(Book).all()
    return render_template('home.html', books=books)

@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        new_book = Book(
            title=request.form['title'],
            author=request.form['author'],
            genre=request.form['genre']
        )
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.session.query(User).filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('home'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = db.session.query(User).filter_by(username=username).first()
        if existing_user:
            flash('Username already exists')
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registered successfully. Please log in.')
            return redirect(url_for('login'))
    return render_template('register.html')

if __name__ == "__main__":
    print("Starting Flask app")
    app.run(debug=True)

