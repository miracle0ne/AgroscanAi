from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    EmailField,
    PasswordField,
    SubmitField
)

from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    EqualTo
)


class RegisterForm(FlaskForm):

    name = StringField(
        "Full Name",
        validators=[
            DataRequired(),
            Length(min=2, max=100)
        ]
    )

    email = EmailField(
        "Email",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    phone = StringField(
        "Phone Number",
        validators=[
            Length(max=30)
        ]
    )

    location = StringField(
        "Location",
        validators=[
            Length(max=150)
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, max=128)
        ]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo(
                "password",
                message="Passwords must match."
            )
        ]
    )

    submit = SubmitField(
        "Create Account"
    )
