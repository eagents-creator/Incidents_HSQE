from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app import db
from app.models import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        print(f"User already authenticated: {current_user.username}")
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"\nLogin attempt:")
        print(f"- Username: {username}")
        
        # Query database for user
        print("Querying database for user...")
        user = User.query.filter_by(username=username).first()
        
        if user is None:
            print("ERROR: User not found in database")
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
        
        print(f"User found:")
        print(f"- ID: {user.id}")
        print(f"- Role: {user.role}")
        print(f"- Is Admin: {user.is_admin}")
        
        # Check password
        print("Checking password...")
        if not user.check_password(password):
            print("ERROR: Invalid password")
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
        
        print("Password verified successfully")
        
        # Log user in
        print("Logging in user...")
        login_user(user, remember=request.form.get('remember_me'))
        print("User logged in successfully")
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        return redirect(next_page)
    
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.email = request.form.get('email')
        if request.form.get('new_password'):
            current_user.set_password(request.form.get('new_password'))
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html')
