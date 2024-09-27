from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from extensions import db
from models.models import Admin, Employee
from sqlalchemy.exc import SQLAlchemyError

main = Blueprint('main', __name__)  # routename = main

@main.route('/', methods=['GET'])
def home():
    return render_template("index.html")

@main.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = Admin.query.filter_by(email=email).first()

    if user and user.password == password:
        session['user_id'] = user.id
        session['user_type'] = 'admin'
        return redirect(url_for('main.admin_dashboard', action='list_employees'))
    else:
        flash('Login failed! Check your credentials and try again.')
        return redirect(url_for('main.home'))

@main.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'user_id' in session and session.get('user_type') == 'admin':
        admin = Admin.query.filter_by(id=session['user_id']).first()
        action = request.args.get('action', 'list_employees')

        if action == 'list_employees':
            employees = Employee.query.all()
            return render_template("admin_dashboard.html", admin=admin, action=action, employees=employees)

        elif action == 'create_employee' and request.method == 'GET':
            return render_template("admin_dashboard.html", admin=admin, action=action)

        elif action == 'create_employee' and request.method == 'POST':
            # Handle employee creation
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')
            age = request.form.get('age')
            position = request.form.get('position')
            picture = request.files.get('picture')

            # Save picture to a folder and get the path
            picture_path = None
            if picture:
                picture_path = f'static/uploads/{picture.filename}'
                picture.save(picture_path)

            new_employee = Employee(
                name=name,
                email=email,
                phone=phone,
                address=address,
                age=age,
                position=position,
                picture=picture_path
            )
            try:
                db.session.add(new_employee)
                db.session.commit()
                flash('Employee created successfully!')
            except SQLAlchemyError as e:
                db.session.rollback()
                flash('Error creating employee.')

            return redirect(url_for('main.admin_dashboard', action='list_employees'))

        elif action == 'update_account' and request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')

            admin.email = email
            if password:
                admin.password = password  # Ensure to hash the password in production

            try:
                db.session.commit()
                flash('Account updated successfully!')
            except SQLAlchemyError:
                db.session.rollback()
                flash('Error updating account.')

            return redirect(url_for('main.admin_dashboard', action='update_account'))

        return render_template("admin_dashboard.html", admin=admin, action=action)
    else:
        return redirect(url_for('main.home'))


@main.route('/delete_employee/<int:employee_id>', methods=['GET'])
def delete_employee(employee_id):
    employee = Employee.query.get(employee_id)
    if employee:
        try:
            db.session.delete(employee)
            db.session.commit()
            flash('Employee deleted successfully!')
        except SQLAlchemyError:
            db.session.rollback()
            flash('Error deleting employee.')
    else:
        flash('Employee not found.')
    return redirect(url_for('main.admin_dashboard', action='list_employees'))

@main.route('/create_employee', methods=['GET', 'POST'])
def create_employee():
    if request.method == 'POST':
        # Handle employee creation logic here
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        age = request.form.get('age')
        position = request.form.get('position')
        picture = request.files.get('picture')

        # Save picture to a folder and get the path
        picture_path = None
        if picture:
            picture_path = f'static/uploads/{picture.filename}'
            picture.save(picture_path)

        new_employee = Employee(
            name=name,
            email=email,
            phone=phone,
            address=address,
            age=age,
            position=position,
            picture=picture_path
        )

        try:
            db.session.add(new_employee)
            db.session.commit()
            flash('Employee created successfully!')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Error creating employee.')

        return redirect(url_for('main.admin_dashboard', action='list_employees'))

    # If GET request, just render the form
    return render_template('admin_dashboard.html', action='create_employee')


@main.route('/update_account', methods=['GET', 'POST'])
def update_account():
    if request.method == 'POST':
        # Handle account update logic here
        email = request.form.get('email')
        password = request.form.get('password')

        # Get the admin account
        admin = Admin.query.filter_by(email='admin@example.com').first()  # Change this as necessary

        if admin:
            admin.email = email
            if password:  # Update password only if provided
                admin.password = password  # Make sure to hash the password before saving

            try:
                db.session.commit()
                flash('Account updated successfully!')
            except SQLAlchemyError as e:
                db.session.rollback()
                flash('Error updating account.')

            return redirect(url_for('main.admin_dashboard', action='update_account'))

    # If GET request, just render the form with current admin data
    admin = Admin.query.filter_by(email='admin@example.com').first()  # Change this as necessary
    return render_template('update_account.html', admin=admin)


@main.route('/edit_employee/<int:employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)

    if request.method == 'POST':
        # Handle employee update logic here
        employee.name = request.form.get('name')
        employee.email = request.form.get('email')
        employee.phone = request.form.get('phone')
        employee.address = request.form.get('address')
        employee.age = request.form.get('age')
        employee.position = request.form.get('position')

        # Handle picture upload if provided
        picture = request.files.get('picture')
        if picture:
            # Save the new picture and update employee record (add your logic here)
            picture_path = f'static/uploads/{picture.filename}'
            picture.save(picture_path)
        try:
            db.session.commit()
            flash('Employee updated successfully!')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Error updating employee.')

        return redirect(url_for('main.admin_dashboard', action='list_employees'))

    return render_template('edit_employee.html', employee=employee)

