from flask import Blueprint, render_template, redirect, url_for, flash, request 
from flask_login import login_user, logout_user, login_required

from app.extensions import db
from app.models.users import User
from app.models.role import Role
from app.auth.forms import RegisterForm

import secrets
import string


auth = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


def generate_user_code():
    characters = string.ascii_uppercase + string.digits

    while True:
        code = "AG-" + "".join(
            secrets.choice(characters)
            for _ in range(5)
        )

        existing_user = User.query.filter_by(
            user_code=code
        ).first()

        if not existing_user:
            return code


@auth.route("/register", methods=["GET", "POST"])
def register():

    form = RegisterForm()

    if form.validate_on_submit():

        email = form.email.data.strip().lower()

        existing_email = User.query.filter_by(
            email=email
        ).first()

        if existing_email:
            flash(
                "An account with this email already exists.",
                "danger"
            )
            return render_template(
                "auth/register.html",
                form=form
            )

        role = Role.query.filter_by(
            name="farmer"
        ).first()

        if not role:
            flash(
                "Farmer role is not configured.",
                "danger"
            )
            return render_template(
                "auth/register.html",
                form=form
            )

        user = User(
            user_code=generate_user_code(),
            name=form.name.data.strip(),
            email=email,
            phone=form.phone.data.strip() or None,
            location=form.location.data.strip() or None,
            role_id=role.id
        )

        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        login_user(user)

        flash(
           "Account created successfully. Please login.",
           "success"
           
        )

        return redirect(
             url_for("auth.login")
        )

    return render_template(
        "auth/register.html",
        form=form
    )


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        user = User.query.filter_by(
            email=email
        ).first()

        if not user or not user.check_password(password):
            flash(
                "Invalid email or password.",
                "danger"
            )
            return render_template(
                "auth/login.html"
            )

        login_user(user)

        return redirect(
            url_for("main.dashboard")
        )

    return render_template(
        "auth/login.html"
    )


@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("main.home")
    )
