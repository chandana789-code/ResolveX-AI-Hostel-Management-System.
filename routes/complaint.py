from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Complaint
from ai.classifier import predict_priority
import os

complaint = Blueprint("complaint", __name__)

UPLOAD_FOLDER = "uploads"


@complaint.route("/raise_complaint", methods=["GET", "POST"])
@login_required
def raise_complaint():

    if request.method == "POST":

        title = request.form["title"]
        category = request.form["category"]
        description = request.form["description"]

        image_name = ""

        image = request.files.get("image")

        if image and image.filename != "":
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            image_name = secure_filename(image.filename)

            image.save(os.path.join(UPLOAD_FOLDER, image_name))

        # -------------------------
        # AI Prediction
        # -------------------------
        try:
            priority = predict_priority(title, description)
            print("=" * 60)
            print("Complaint Submitted")
            print("Title       :", title)
            print("Description :", description)
            print("Predicted Priority :", priority)
            print("=" * 60)

        except Exception as e:
            print("Prediction Error:", e)
            priority = "Medium"

        # -------------------------
        # Save Complaint
        # -------------------------
        new_complaint = Complaint(
            student_id=current_user.id,
            title=title,
            category=category,
            description=description,
            image=image_name,
            status="Pending",
            priority=priority
        )

        db.session.add(new_complaint)
        db.session.commit()

        flash("Complaint submitted successfully!", "success")

        return redirect(url_for("complaint.complaint_history"))

    return render_template("raise_complaint.html")


@complaint.route("/complaint_history")
@login_required
def complaint_history():

    complaints = Complaint.query.filter_by(
        student_id=current_user.id
    ).order_by(
        Complaint.created_at.desc()
    ).all()

    return render_template(
        "complaint_history.html",
        complaints=complaints
    )