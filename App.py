from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# SQLite configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    clinic_name = db.Column(db.String(100), nullable=True)
    specialization = db.Column(db.String(100), nullable=True)
    password = db.Column(db.String(200), nullable=False)

# Manually create tables when app starts up
with app.app_context():
    db.create_all()

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists!'}), 400

    hashed_password = generate_password_hash(data['password'], method='sha256')
    user = User(
        first_name=data['firstName'],
        last_name=data['lastName'],
        email=data['email'],
        phone_number=data['phoneNumber'],
        clinic_name=data['clinicName'],
        specialization=data['specialization'],
        password=hashed_password
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully!'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Login successful!'}), 200
    return jsonify({'message': 'Invalid email or password!'}), 401

if __name__ == '__main__':
    app.run(debug=True)
