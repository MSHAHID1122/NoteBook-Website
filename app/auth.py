from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from .models import Users
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = Users.query.filter_by(email=email).first()
        
        if user:
            flash('Email address already exists')
            return redirect(url_for('auth.signup'))
        
        new_user = Users(name=name, email=email, password=password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('main.Index'))
        except IntegrityError:
            db.session.rollback()
            flash('Email already exists or data is invalid')
            return render_template('signup.html')
    
    return render_template('signup.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = Users.query.filter_by(email=email).first()
        
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('main.Index'))
        else:
            flash('Invalid email or password')
    
    return render_template('login.html')

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
