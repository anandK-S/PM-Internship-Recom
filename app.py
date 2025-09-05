import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import sqlite3
import json
import requests
from models.database import init_db, get_db
from models.user import User
from models.internship import Internship
from models.application import Application
from services.recommendation_engine import RecommendationEngine
from services.external_api import fetch_external_internships
from utils.helpers import allowed_file, save_file

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt_dev_key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Initialize JWT
jwt = JWTManager(app)

# Initialize database
with app.app_context():
    init_db()

# Initialize recommendation engine
recommendation_engine = RecommendationEngine()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Authentication routes
@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user already exists
        db = get_db()
        existing_user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        
        if existing_user:
            flash('Email already registered', 'error')
            return render_template('auth/register.html')
        
        # Create new user
        hashed_password = generate_password_hash(password)
        db.execute(
            'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
            (username, email, hashed_password)
        )
        db.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html')

@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        
        if user and check_password_hash(user['password'], password):
            # Create access token
            access_token = create_access_token(identity=user['id'])
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['access_token'] = access_token
            
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html')

@app.route('/auth/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/auth/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        
        if user:
            # In a real application, send a password reset email
            # For this prototype, we'll just show a success message
            flash('Password reset instructions sent to your email', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email not found', 'error')
    
    return render_template('auth/forgot_password.html')

# User profile routes
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    db = get_db()
    
    if request.method == 'POST':
        # Update user profile
        education = request.form.get('education')
        skills = request.form.get('skills')
        interests = request.form.get('interests')
        location = request.form.get('location')
        
        db.execute(
            '''UPDATE users SET 
               education = ?, 
               skills = ?, 
               interests = ?, 
               location = ? 
               WHERE id = ?''',
            (education, skills, interests, location, user_id)
        )
        db.commit()
        
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))
    
    # Get user profile data
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    return render_template('profile/profile.html', user=user)

# Internship routes
@app.route('/internships')
def internships():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    local_internships = db.execute('SELECT * FROM internships').fetchall()
    
    # Get external internships (in a real app, implement caching)
    try:
        external_internships = fetch_external_internships()
    except Exception as e:
        external_internships = []
        print(f"Error fetching external internships: {e}")
    
    all_internships = list(local_internships) + external_internships
    
    return render_template('internships/list.html', internships=all_internships)

@app.route('/internships/recommendations')
def recommendations():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if not user['skills'] or not user['interests']:
        flash('Please complete your profile to get recommendations', 'warning')
        return redirect(url_for('profile'))
    
    # Get all internships
    local_internships = db.execute('SELECT * FROM internships').fetchall()
    
    try:
        external_internships = fetch_external_internships()
    except Exception as e:
        external_internships = []
        print(f"Error fetching external internships: {e}")
    
    all_internships = list(local_internships) + external_internships
    
    # Get recommendations
    recommended_internships = recommendation_engine.get_recommendations(
        user, 
        all_internships,
        limit=5
    )
    
    return render_template(
        'internships/recommendations.html', 
        internships=recommended_internships
    )

@app.route('/internships/<int:internship_id>')
def internship_detail(internship_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    internship = db.execute('SELECT * FROM internships WHERE id = ?', (internship_id,)).fetchone()
    
    if not internship:
        flash('Internship not found', 'error')
        return redirect(url_for('internships'))
    
    return render_template('internships/detail.html', internship=internship)

@app.route('/internships/apply/<int:internship_id>', methods=['GET', 'POST'])
def apply_internship(internship_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    db = get_db()
    
    # Check if internship exists
    internship = db.execute('SELECT * FROM internships WHERE id = ?', (internship_id,)).fetchone()
    
    if not internship:
        flash('Internship not found', 'error')
        return redirect(url_for('internships'))
    
    # Check if already applied
    existing_application = db.execute(
        'SELECT * FROM applications WHERE user_id = ? AND internship_id = ?',
        (user_id, internship_id)
    ).fetchone()
    
    if existing_application:
        flash('You have already applied for this internship', 'warning')
        return redirect(url_for('my_applications'))
    
    if request.method == 'POST':
        # Process application
        cover_letter = request.form.get('cover_letter')
        resume = request.files.get('resume')
        
        # Save resume if provided
        resume_path = None
        if resume and allowed_file(resume.filename):
            resume_path = save_file(resume, app.config['UPLOAD_FOLDER'])
        
        # Create application
        db.execute(
            'INSERT INTO applications (user_id, internship_id, cover_letter, resume_path, status, applied_date) VALUES (?, ?, ?, ?, ?, ?)',
            (user_id, internship_id, cover_letter, resume_path, 'Applied', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )
        db.commit()
        
        flash('Application submitted successfully', 'success')
        return redirect(url_for('my_applications'))
    
    return render_template('internships/apply.html', internship=internship)

@app.route('/applications')
def my_applications():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    db = get_db()
    
    applications = db.execute(
        '''SELECT a.*, i.title, i.company 
           FROM applications a
           JOIN internships i ON a.internship_id = i.id
           WHERE a.user_id = ?
           ORDER BY a.applied_date DESC''',
        (user_id,)
    ).fetchall()
    
    return render_template('internships/applications.html', applications=applications)

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    db = get_db()
    
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    # Get application statistics
    application_stats = db.execute(
        '''SELECT status, COUNT(*) as count 
           FROM applications 
           WHERE user_id = ? 
           GROUP BY status''',
        (user_id,)
    ).fetchall()
    
    # Convert to dictionary for easier access in template
    stats = {row['status']: row['count'] for row in application_stats}
    
    # Get recent applications
    recent_applications = db.execute(
        '''SELECT a.*, i.title, i.company 
           FROM applications a
           JOIN internships i ON a.internship_id = i.id
           WHERE a.user_id = ?
           ORDER BY a.applied_date DESC
           LIMIT 5''',
        (user_id,)
    ).fetchall()
    
    # Check if profile is complete
    profile_complete = all([
        user['education'],
        user['skills'],
        user['interests'],
        user['location']
    ])
    
    return render_template(
        'dashboard.html',
        user=user,
        stats=stats,
        recent_applications=recent_applications,
        profile_complete=profile_complete
    )

# API routes
@app.route('/api/internships')
@jwt_required()
def api_internships():
    db = get_db()
    internships = db.execute('SELECT * FROM internships').fetchall()
    
    # Convert to list of dicts
    result = []
    for internship in internships:
        result.append({
            'id': internship['id'],
            'title': internship['title'],
            'company': internship['company'],
            'location': internship['location'],
            'description': internship['description'],
            'requirements': internship['requirements'],
            'stipend': internship['stipend'],
            'duration': internship['duration'],
            'deadline': internship['deadline']
        })
    
    return jsonify(result)

@app.route('/api/recommendations')
@jwt_required()
def api_recommendations():
    user_id = get_jwt_identity()
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get all internships
    local_internships = db.execute('SELECT * FROM internships').fetchall()
    
    try:
        external_internships = fetch_external_internships()
    except Exception as e:
        external_internships = []
        print(f"Error fetching external internships: {e}")
    
    all_internships = list(local_internships) + external_internships
    
    # Get recommendations
    recommended_internships = recommendation_engine.get_recommendations(
        user, 
        all_internships,
        limit=5
    )
    
    # Convert to list of dicts
    result = []
    for internship, score in recommended_internships:
        result.append({
            'id': internship['id'],
            'title': internship['title'],
            'company': internship['company'],
            'location': internship['location'],
            'description': internship['description'],
            'requirements': internship['requirements'],
            'stipend': internship['stipend'],
            'duration': internship['duration'],
            'deadline': internship['deadline'],
            'match_score': score,
            'match_reason': internship.get('match_reason', 'Good match based on your profile')
        })
    
    return jsonify(result)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)