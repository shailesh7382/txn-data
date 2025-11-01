from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from .extensions import db
from .models import User

def register_routes(app):
    @app.route("/")
    def index():
        return redirect(url_for("list_users"))

    @app.route("/users")
    def list_users():
        q = (request.args.get("q") or "").strip()
        query = User.query
        if q:
            like = f"%{q}%"
            query = query.filter(or_(User.full_name.ilike(like), User.email.ilike(like)))
        users = query.order_by(User.created_at.desc()).all()
        return render_template("list_users.html", users=users, q=q)

    @app.route("/users/new", methods=["GET", "POST"])
    def create_user():
        if request.method == "POST":
            full_name = (request.form.get("full_name") or "").strip()
            email = (request.form.get("email") or "").strip().lower()

            errors = []
            if not full_name:
                errors.append("Full name is required.")
            if not email:
                errors.append("Email is required.")
            elif "@" not in email or "." not in email.split("@")[-1]:
                errors.append("Email format looks invalid.")

            if not errors and User.query.filter_by(email=email).first():
                errors.append("A user with this email already exists.")

            if errors:
                for e in errors:
                    flash(e, "error")
                return render_template("create_user.html", values={"full_name": full_name, "email": email})

            user = User(full_name=full_name, email=email)
            db.session.add(user)
            db.session.commit()
            flash("User created successfully.", "success")
            return redirect(url_for("list_users"))

        return render_template("create_user.html", values={})

    @app.route("/users/<int:user_id>/delete", methods=["POST"])
    def delete_user(user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        flash("User deleted.", "success")
        return redirect(url_for("list_users"))

