from app import app
from models import db, Admin

with app.app_context():

    admin = Admin.query.filter_by(username="admin").first()

    if admin is None:

        admin = Admin(
            username="admin",
            password="admin123"
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin created successfully!")

    else:
        print("Admin already exists.")
