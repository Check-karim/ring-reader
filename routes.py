from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from extensions import db
from models.models import Admin
from sqlalchemy.exc import SQLAlchemyError

main = Blueprint('main', __name__)  # routename= main

@main.route('/', methods=['GET'])
def home():
    return render_template("index.html")

@main.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    user_type = request.form.get('user_type')

    user = Admin.query.filter_by(email=email).first()

    if user and user.password == password:
        session['user_id'] = user.id

        return redirect(url_for('main.admin_dashboard'))
    else:
        flash('Login failed! Check your credentials and try again.')
        return redirect(url_for('main.home'))

@main.route('/admin_dashboard', methods=['GET'])
def admin_dashboard():
    if 'user_id' in session and session.get('user_type') == 'admin':
        admin = Admin.query.filter_by(id=session['user_id']).first()
        return render_template("admin_dashboard.html", admin=admin)
    else:
        return redirect(url_for('main.home'))