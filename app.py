from flask import Flask, render_template, flash, url_for, redirect
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from database import db
from forms import RegisterForm, LoginForm, TodoForm
from models import User, Task
from dotenv import load_dotenv
import os


app = Flask(__name__)
bootstrap = Bootstrap(app)

# Login configuration
login_manager = LoginManager()
login_manager.init_app(app)


USER_DB = 'postgres'
PASS_DB = 'admin'
URL_DB = 'localhost:5432'
NAME_DB = 'todo_list_db'
FULL_URL_DB = f'postgresql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', FULL_URL_DB)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

load_dotenv('env')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db.init_app(app)

with app.app_context():
    db.create_all()

# Configure flask-migrate
migrate = Migrate()
migrate.init_app(app, db)


@app.route('/')
def home():
    return render_template('index.html')


# Register to page
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            print(User.query.filter_by(email=form.email.data).first())

            flash(f"Hi {form.name.data} You have already signed up with that email, log in instead!")
            return render_template('login.html')

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )

        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=hash_and_salted_password
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)

        return redirect(url_for('todo_list'))

    return render_template('register.html', form=form)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('todo_list'))
        else:
            flash('Please enter the correct credentials')

    return render_template('login.html', form=form)


# User logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


# User to-do list profile
@app.route('/todo', methods=['GET', 'POST'])
def todo_list():
    form = TodoForm()
    tasks = Task.query.all()

    if form.validate_on_submit():
        todo_text = Task(
            task_todo=form.text.data.title(),
            date=datetime.utcnow(),
            user_id=current_user.id
        )
        db.session.add(todo_text)
        db.session.commit()
        tasks = Task.query.all()
        form.text.data = ''

        return render_template('todo.html', form=form, tasks=tasks, current_user=current_user, todo_text=todo_text)

    return render_template('todo.html', form=form, tasks=tasks)


# Delete a specific task
@app.route('/delete/<int:task_id>')
def delete(task_id):
    task_to_delete = Task.query.get(task_id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for('todo_list'))


if __name__ == '__main__':
    app.run()
