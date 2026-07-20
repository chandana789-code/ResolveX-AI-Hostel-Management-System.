from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


# ==========================
# Student Table
# ==========================
class Student(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), unique=True, nullable=False)

    password = db.Column(db.String(200), nullable=False)

    roll_no = db.Column(db.String(20), unique=True)

    hostel_block = db.Column(db.String(20))

    room_no = db.Column(db.String(20))


# ==========================
# Admin Table
# ==========================
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), unique=True, nullable=False)

    password = db.Column(db.String(200), nullable=False)


# ==========================
# Room Table
# ==========================
class Room(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    room_number = db.Column(db.String(20), unique=True, nullable=False)

    block = db.Column(db.String(20), nullable=False)

    capacity = db.Column(db.Integer, nullable=False)

    occupied = db.Column(db.Integer, default=0)

    vacant = db.Column(db.Integer)

    status = db.Column(db.String(20), default="Vacant")


# ==========================
# Complaint Table
# ==========================
class Complaint(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id")
    )

    student = db.relationship("Student", backref="complaints")

    title = db.Column(db.String(100))

    description = db.Column(db.Text)

    category = db.Column(db.String(50))

    image = db.Column(db.String(200))

    status = db.Column(db.String(30), default="Pending")

    priority = db.Column(db.String(20), default="Medium")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
class RoomRequest(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id")
    )

    current_room = db.Column(db.String(20))

    requested_room = db.Column(db.String(20))

    reason = db.Column(db.Text)

    status = db.Column(
        db.String(20),
        default="Pending"
    )

    student = db.relationship("Student")
