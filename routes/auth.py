from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)
from models import db, Student, RoomRequest


auth = Blueprint("auth", __name__)

bcrypt = None


# -----------------------------
# Register
# -----------------------------
@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        roll_no = request.form["roll_no"]
        hostel_block = request.form["hostel_block"]
        room_no = request.form["room_no"]
        password = request.form["password"]

        if Student.query.filter_by(email=email).first():
            return "Email already exists"

        if Student.query.filter_by(roll_no=roll_no).first():
            return "Roll Number already exists"

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        student = Student(
            name=name,
            email=email,
            roll_no=roll_no,
            hostel_block=hostel_block,
            room_no=room_no,
            password=hashed_password
        )

        db.session.add(student)
        db.session.commit()

        return redirect(url_for("auth.login"))

    return render_template("register.html")


# -----------------------------
# Login
# -----------------------------
@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        student = Student.query.filter_by(email=email).first()

        if student and bcrypt.check_password_hash(student.password, password):

            login_user(student)

            return redirect(url_for("auth.dashboard"))

        return "Invalid Email or Password"

    return render_template("login.html")


# -----------------------------
# Student Dashboard
# -----------------------------
@auth.route("/student_dashboard")
@login_required
def dashboard():

    room_request = RoomRequest.query.filter_by(
        student_id=current_user.id
    ).order_by(RoomRequest.id.desc()).first()

    return render_template(
        "student_dashboard.html",
        room_request=room_request
    )


# -----------------------------
# Logout
# -----------------------------
@auth.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("auth.login"))