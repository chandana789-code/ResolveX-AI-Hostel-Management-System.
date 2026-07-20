from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Complaint, Admin, RoomRequest, Room, Student
from werkzeug.security import check_password_hash

admin = Blueprint("admin", __name__)


# ==========================
# Admin Login
# ==========================
@admin.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"].strip()

        admin_user = Admin.query.filter_by(username=username).first()

        if admin_user and check_password_hash(admin_user.password, password):
            return redirect(url_for("admin.admin_dashboard"))

        return "Invalid Admin Credentials"

    return render_template("admin_login.html")


# ==========================
# Admin Dashboard
# ==========================
@admin.route("/admin_dashboard")
def admin_dashboard():

    complaints = Complaint.query.order_by(
        Complaint.created_at.desc()
    ).all()

    return render_template(
        "admin_dashboard.html",
        complaints=complaints
    )
@admin.route("/admin_rooms")
def admin_rooms():

    rooms = Room.query.order_by(
        Room.block,
        Room.room_number
    ).all()

    students = Student.query.all()

    return render_template(
    "rooms.html",
    rooms=rooms,
    students=students,
    is_admin=True,
    request_map={}
)


# ==========================
# Complaint Status
# ==========================
@admin.route("/update_status/<int:id>/<status>")
def update_status(id, status):

    complaint = Complaint.query.get_or_404(id)

    complaint.status = status

    db.session.commit()

    return redirect(url_for("admin.admin_dashboard"))


# ===================================================
# ROOM CHANGE REQUESTS
# ===================================================
@admin.route("/room_requests")
def room_requests():

    requests = RoomRequest.query.all()

    return render_template(
        "room_requests.html",
        requests=requests
    )


# ===================================================
# APPROVE ROOM REQUEST
# ===================================================
@admin.route("/approve_request/<int:id>")
def approve_request(id):

    req = RoomRequest.query.get_or_404(id)

    student = Student.query.get(req.student_id)

    old_room = Room.query.filter_by(
        room_number=req.current_room
    ).first()

    new_room = Room.query.filter_by(
        room_number=req.requested_room
    ).first()

    # Remove from old room
    if old_room:

        old_room.occupied = max(0, old_room.occupied - 1)

        old_room.vacant = old_room.capacity - old_room.occupied

        if old_room.vacant == 0:
            old_room.status = "Full"
        else:
            old_room.status = "Vacant"

    # Allocate new room
    if new_room:

        if new_room.occupied < new_room.capacity:

            new_room.occupied += 1

        new_room.vacant = new_room.capacity - new_room.occupied

        if new_room.vacant == 0:
            new_room.status = "Full"
        else:
            new_room.status = "Vacant"

    student.room_no = req.requested_room
    student.hostel_block = new_room.block

    req.status = "Approved"

    db.session.commit()

    return redirect(url_for("admin.room_requests"))


# ===================================================
# REJECT ROOM REQUEST
# ===================================================
@admin.route("/reject_request/<int:id>")
def reject_request(id):

    req = RoomRequest.query.get_or_404(id)

    req.status = "Rejected"

    db.session.commit()

    return redirect(url_for("admin.room_requests"))