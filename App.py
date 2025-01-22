from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_cors import CORS
import csv
from io import StringIO

# Initialize Flask app and extensions
app = Flask(__name__)
CORS(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<User {self.first_name} {self.last_name}>"

# Route for Signup
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    first_name = data.get('firstName')
    last_name = data.get('lastName')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirmPassword')

    # Validate required fields
    if not all([first_name, last_name, email, password, confirm_password]):
        return jsonify({"message": "All fields are required!"}), 400

    # Check if passwords match
    if password != confirm_password:
        return jsonify({"message": "Passwords do not match!"}), 400

    # Check if email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists!"}), 400

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Create a new user
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password_hash=hashed_password
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Signup successful!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred. Please try again later."}), 500

# Route for Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    # Validate required fields
    if not all([email, password]):
        return jsonify({"message": "Email and password are required!"}), 400

    user = User.query.filter_by(email=email).first()

    # Validate user credentials
    if user and bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"message": "Login successful!"}), 200

    return jsonify({"message": "Invalid email or password!"}), 401

# Route to Download User Data as CSV
@app.route('/download-users', methods=['GET'])
def download_users():
    # Query all user data
    users = User.query.all()

    # Create an in-memory CSV file
    csv_data = StringIO()
    csv_writer = csv.writer(csv_data)

    # Write CSV headers
    csv_writer.writerow(['ID', 'First Name', 'Last Name', 'Email'])

    # Write user data rows
    for user in users:
        csv_writer.writerow([user.id, user.first_name, user.last_name, user.email])

    # Prepare the response
    csv_data.seek(0)  # Move to the start of the CSV data
    response = Response(csv_data.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=users.csv'

    return response

if __name__ == '__main__':
    app.run(debug=True)
