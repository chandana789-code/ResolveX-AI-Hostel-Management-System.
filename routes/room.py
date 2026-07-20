from flask import Blueprint, render_template, request, redirect, url_for

from models import db, Room, Student, Admin
from flask_login import login_required, current_user
from models import RoomRequest

room = Blueprint("room", __name__)


# -------------------------------
# View All Rooms
# -------------------------------
@room.route("/rooms")
@login_required
def rooms():

    rooms = Room.query.order_by(
        Room.block,
        Room.room_number
    ).all()

    # Correct occupied, vacant and status values
    for room in rooms:

        if room.occupied < 0:
            room.occupied = 0

        if room.occupied > room.capacity:
            room.occupied = room.capacity

        room.vacant = room.capacity - room.occupied

        if room.vacant <= 0:
            room.vacant = 0
            room.status = "Full"
        else:
            room.status = "Vacant"

    db.session.commit()

    # Detect whether the logged-in user is an admin
    is_admin = isinstance(current_user, Admin)

    request_map = {}

    if not is_admin:
        requests = RoomRequest.query.filter_by(
        student_id=current_user.id
    ).all()

    for req in requests:
        request_map[req.requested_room] = req.status

    return render_template(
    "rooms.html",
    rooms=rooms,
    is_admin=is_admin,
    request_map=request_map
)

# -------------------------------
# Add Room
# -------------------------------
@room.route("/add_room", methods=["GET", "POST"])
def add_room():

    if request.method == "POST":

        # Get form data
        room_number = int(request.form["room_number"])
        block = request.form["block"]
        capacity = int(request.form["capacity"])

        # -------------------------------
        # Block-wise Room Range Validation
        # -------------------------------
        ranges = {
            "A Block": (101, 150),
            "B Block": (201, 250),
            "C Block": (301, 350),
            "D Block": (401, 450)
        }

        start, end = ranges[block]

        if room_number < start or room_number > end:
            return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Invalid Room Number</title>

<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css" rel="stylesheet">

<style>

body{{
background:linear-gradient(135deg,#eef6ff,#f8fbff);
height:100vh;
display:flex;
justify-content:center;
align-items:center;
font-family:'Poppins',sans-serif;
}}

.card{{
width:550px;
border:none;
border-radius:25px;
box-shadow:0 15px 40px rgba(0,0,0,.12);
overflow:hidden;
}}

.card-header{{
background:linear-gradient(135deg,#ef4444,#dc2626);
color:white;
padding:25px;
text-align:center;
}}

.icon{{
font-size:65px;
}}

.card-body{{
padding:40px;
text-align:center;
}}

.range{{
background:#eef6ff;
padding:18px;
border-radius:15px;
font-size:20px;
font-weight:600;
margin:25px 0;
}}

.btn-custom{{
padding:12px 30px;
border-radius:30px;
font-weight:600;
}}

</style>

</head>

<body>

<div class="card">

<div class="card-header">

<div class="icon">
❌
</div>

<h2 class="fw-bold mt-2">
Invalid Room Number
</h2>

</div>

<div class="card-body">

<p class="fs-5 text-secondary">

The room number you entered does not belong to the selected hostel block.

</p>

<div class="range">

🏠 <b>{block}</b><br>

Allowed Room Numbers

<h3 class="mt-2 text-primary">
{start} - {end}
</h3>

</div>

<a href="/add_room" class="btn btn-primary btn-custom">

<i class="bi bi-arrow-left-circle"></i>

Go Back

</a>

</div>

</div>

</body>
</html>
"""

        # -------------------------------
        # Check Duplicate Room
        # -------------------------------
        existing = Room.query.filter_by(
            room_number=str(room_number)
        ).first()

        if existing:
           return f"""
<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">

<title>Room Exists</title>

<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css" rel="stylesheet">

<style>

body{{
background:linear-gradient(135deg,#eef6ff,#f8fbff);
height:100vh;
display:flex;
justify-content:center;
align-items:center;
font-family:'Poppins',sans-serif;
}}

.card{{
width:520px;
border:none;
border-radius:25px;
box-shadow:0 15px 40px rgba(0,0,0,.12);
}}

.card-header{{
background:linear-gradient(135deg,#f59e0b,#d97706);
color:white;
padding:25px;
text-align:center;
}}

.card-body{{
padding:40px;
text-align:center;
}}

</style>

</head>

<body>

<div class="card">

<div class="card-header">

<h2>
⚠ Room Already Exists
</h2>

</div>

<div class="card-body">

<p class="fs-5">

Room <b>{room_number}</b> already exists in the database.

</p>

<a href="/add_room" class="btn btn-warning rounded-pill px-4">

<i class="bi bi-arrow-left-circle"></i>

Go Back

</a>

</div>

</div>

</body>

</html>
"""

        # -------------------------------
        # Create Room
        # -------------------------------
        room = Room(
            room_number=str(room_number),
            block=block,
            capacity=capacity,
            occupied=0,
            vacant=capacity,
            status="Vacant"
        )

        db.session.add(room)
        db.session.commit()

        return redirect(url_for("admin.admin_rooms"))

    return render_template("add_room.html")


# -------------------------------
# Allocate Room
# -------------------------------
@room.route("/allocate_room/<int:student_id>/<int:room_id>")
def allocate_room(student_id, room_id):

    student = Student.query.get_or_404(student_id)

    room = Room.query.get_or_404(room_id)

    if room.vacant > 0:

        # Remove from old room
        if student.room_no:

            old_room = Room.query.filter_by(
                room_number=student.room_no
            ).first()

            if old_room:

                old_room.occupied = max(0, old_room.occupied - 1)
                old_room.vacant = old_room.capacity - old_room.occupied

                if old_room.vacant > 0:
                    old_room.status = "Vacant"

        # Allocate new room
        student.room_no = room.room_number
        student.hostel_block = room.block

        if room.occupied < room.capacity:
            room.occupied += 1

        room.vacant = room.capacity - room.occupied

        if room.vacant == 0:
            room.status = "Full"
        else:
            room.status = "Vacant"

        db.session.commit()

    return redirect(url_for("room.rooms"))
# -------------------------------
# Student Request Room Change
# -------------------------------
@room.route("/request_room/<int:room_id>", methods=["GET", "POST"])
@login_required
def request_room(room_id):

    room = Room.query.get_or_404(room_id)

    # Don't allow requests if room is already full
    if room.occupied >= room.capacity:
        return "Room is already full."

    if request.method == "POST":

        reason = request.form["reason"]

        # Prevent duplicate pending request for the same room
        existing = RoomRequest.query.filter_by(
            student_id=current_user.id,
            requested_room=room.room_number,
            status="Pending"
        ).first()

        if existing:
            return "You have already requested this room."

        request_data = RoomRequest(
            student_id=current_user.id,
            current_room=current_user.room_no,
            requested_room=room.room_number,
            reason=reason,
            status="Pending"
        )

        db.session.add(request_data)
        db.session.commit()

        return redirect(url_for("auth.dashboard"))

    return render_template(
        "request_room.html",
        room=room
    )