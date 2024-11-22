from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from models import db, User, Patient, Doctor, Appointment  # Import models
from forms import PatientForm, DoctorForm, AppointmentForm, RegistrationForm, LoginForm
from flask import jsonify

# Create Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_SECRET_KEY'] = 'your-secret-key'

# Initialize the SQLAlchemy instance
db.init_app(app)  # Initialize db with the Flask app
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirect to login page if unauthorized

# Enable CSRF protection
csrf = CSRFProtect(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Error handler for 404
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

# app.py (registration route)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))  # Redirect if already logged in
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists. Please login.', 'danger')
            return redirect(url_for('register'))
        
        new_user = User(
            username=form.username.data,
            password=generate_password_hash(form.password.data),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            age=form.age.data,
            gender=form.gender.data,
            email=form.email.data,
            phone=form.phone.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))  # Redirect if already logged in
    form = LoginForm()
    
    # If form is valid
    if form.validate_on_submit():
        # Fetch user by username from the database
        user = User.query.filter_by(username=form.username.data).first()

        # Check if the user exists and the password is correct
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            # Flash error if login fails
            flash('Login unsuccessful. Please check your username and password.', 'danger')
    
    # If login failed or request is GET
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html')

# Route for home page
@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')  # Show home page if logged in
    else:
        return redirect(url_for('login'))  # Redirect to login if not logged in

# Route for registering a patient
@app.route('/register-patient', methods=['GET', 'POST'])
def register_patient():
    form = PatientForm()
    if form.validate_on_submit():
        new_patient = Patient(
            name=form.name.data,
            age=form.age.data,
            contact=form.contact.data,
            address=form.address.data
        )
        db.session.add(new_patient)
        db.session.commit()
        flash('Patient Registered Successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('register_patient.html', form=form)

# Route to discharge a patient
@app.route('/discharge_patient/<int:id>', methods=['POST'])
def discharge_patient(id):
    patient = Patient.query.get_or_404(id)
    db.session.delete(patient)
    db.session.commit()
    flash('Patient successfully discharged.', 'success')
    return redirect(url_for('index'))

@app.route('/delete_doctor/<int:doctor_id>', methods=['POST'])
def delete_doctor(doctor_id):
    try:
        doctor = Doctor.query.get(doctor_id)
        if doctor:
            db.session.delete(doctor)
            db.session.commit()
            print(f"Doctor with ID {doctor_id} deleted successfully.")
            return jsonify({"success": True})  # Success message
        else:
            print(f"Doctor with ID {doctor_id} not found.")
            return jsonify({"success": False}), 404  # Not found error
    except Exception as e:
        print(f"Error deleting doctor: {e}")
        return jsonify({"success": False}), 500  # Internal server error



# Route for searching a patient by ID
@app.route('/search-patient')
def search_patient():
    patient_id = request.args.get('id')
    if patient_id:
        patient = Patient.query.filter_by(id=patient_id).first()
        if patient:
            return render_template('patients_table.html', patients=[patient])
        else:
            flash('Patient not found!', 'danger')
            return render_template('patients_table.html', patients=[])
    return redirect(url_for('index'))

# Route for searching doctors
@app.route('/search-doctor')
def search_doctor():
    doctor_id = request.args.get('id')
    if doctor_id:
        doctor = Doctor.query.filter_by(id=doctor_id).first()
        if doctor:
            return render_template('doctors.html', doctors=[doctor])
        else:
            flash('Doctor not found!', 'danger')
            return render_template('doctors.html', doctors=[])
    return redirect(url_for('doctors'))

# Route for listing doctors
@app.route('/doctors')
def doctors():
    doctor_list = Doctor.query.all()
    return render_template('doctors.html', doctors=doctor_list)

# Route to add a new doctor
@app.route('/add-doctor', methods=['GET', 'POST'])
def add_doctor():
    form = DoctorForm()
    if form.validate_on_submit():
        new_doctor = Doctor(
            name=form.name.data,
            specialization=form.specialization.data,
            contact=form.contact.data
        )
        db.session.add(new_doctor)
        db.session.commit()
        flash('Doctor added successfully!', 'success')
        return redirect(url_for('doctors'))
    
    return render_template('add_doctor.html', form=form)

# Route for updating doctor details
@app.route('/update-doctor/<int:doctor_id>', methods=['GET', 'POST'])
def update_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    form = DoctorForm(obj=doctor)
    
    if form.validate_on_submit():
        doctor.name = form.name.data
        doctor.specialization = form.specialization.data
        doctor.contact = form.contact.data
        db.session.commit()
        flash('Doctor details updated successfully!', 'success')
        return redirect(url_for('doctors'))

    return render_template('add_doctor.html', form=form, doctor=doctor)

# Route for fetching registered patients
@app.route('/get-patients')
def get_patients():
    patients = Patient.query.all()
    return render_template('patients_table.html', patients=patients)

# Route for updating patient details
@app.route('/update-patient/<int:id>', methods=['GET', 'POST'])
def update_patient(id):
    patient = Patient.query.get_or_404(id)
    form = PatientForm(obj=patient)
    
    if form.validate_on_submit():
        patient.name = form.name.data
        patient.age = form.age.data
        patient.contact = form.contact.data
        patient.address = form.address.data
        db.session.commit()
        flash('Patient details updated successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('register_patient.html', form=form)

@app.route('/appointment', methods=['GET', 'POST'])
@app.route('/appointment/<int:appointment_id>', methods=['GET', 'POST'])
def appointment(appointment_id=None):
    if appointment_id:
        # Retrieve the existing appointment if editing
        appointment = Appointment.query.get_or_404(appointment_id)
        form = AppointmentForm(obj=appointment)  # Pre-fill form with appointment data
    else:
        appointment = None
        form = AppointmentForm()
    
    # Populate choices for the form fields
    form.patient_id.choices = [(p.id, p.name) for p in Patient.query.all()]
    form.doctor_id.choices = [(d.id, d.name) for d in Doctor.query.all()]
    
    if form.validate_on_submit():
        if appointment:
            # Update existing appointment
            appointment.patient_id = form.patient_id.data
            appointment.doctor_id = form.doctor_id.data
            appointment.appointment_date = form.appointment_date.data
            flash('Appointment updated successfully!', 'success')
        else:
            # Create new appointment if not editing
            appointment = Appointment(
                patient_id=form.patient_id.data,
                doctor_id=form.doctor_id.data,
                appointment_date=form.appointment_date.data
            )
            db.session.add(appointment)
            flash('Appointment scheduled successfully!', 'success')
        
        db.session.commit()
        return redirect(url_for('appointment_table'))

    return render_template('appointment.html', form=form, appointment=appointment)

@app.route('/appointments')
def appointment_table():
    appointments = Appointment.query.all()
    return render_template('appointment_table.html', appointments=appointments)


@csrf.exempt
@app.route('/discharge-appointment/<int:appointment_id>', methods=['POST'])
def discharge_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    flash('Appointment discharged successfully!', 'success')
    return jsonify(success=True), 200



@app.route('/update_details', methods=['POST'])
@login_required
def update_details():
    # Retrieve current user's record
    user = User.query.get(current_user.id)
    if user:
        # Update user details from form data
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.age = request.form['age']
        user.gender = request.form['gender']
        user.email = request.form['email']
        user.phone = request.form['phone']
        
        # Commit the changes to the database
        db.session.commit()
        flash('Profile updated successfully!', 'success')
    else:
        flash('User not found!', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
