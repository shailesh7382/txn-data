from datetime import datetime
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

# File-based SQLite DB (users.db in project root)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --- Model ---
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<User {self.id} {self.email}>"

# Create tables if missing
with app.app_context():
    db.create_all()

# --- Routes ---
@app.route("/")
def index():
    return redirect(url_for("list_users"))

@app.route("/users")
def list_users():
    q = request.args.get("q", "").strip()
    query = User.query
    if q:
        like = f"%{q}%"
        query = query.filter(db.or_(User.full_name.ilike(like), User.email.ilike(like)))
    users = query.order_by(User.created_at.desc()).all()
    return render_template("list_users.html", users=users, q=q)

@app.route("/users/new", methods=["GET", "POST"])
def create_user():
    if request.method == "POST":
        full_name = (request.form.get("full_name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()

        # basic validation
        errors = []
        if not full_name:
            errors.append("Full name is required.")
        if not email:
            errors.append("Email is required.")
        elif "@" not in email or "." not in email.split("@")[-1]:
            errors.append("Email format looks invalid.")

        # email uniqueness check
        if not errors and User.query.filter_by(email=email).first():
            errors.append("A user with this email already exists.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("create_user.html", values={"full_name": full_name, "email": email})

        # create + save
        user = User(full_name=full_name, email=email)
        db.session.add(user)
        db.session.commit()
        flash("User created successfully.", "success")
        return redirect(url_for("list_users"))

    return render_template("create_user.html", values={})

# Simple delete (optional)
@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted.", "success")
    return redirect(url_for("list_users"))

if __name__ == "__main__":
    # Run: python app.py
    app.run(debug=True)
