from flask_wtf import FlaskForm
from wtforms.fields import EmailField, StringField, PasswordField
from wtforms.validators import Email, DataRequired, ValidationError, Length

from .models import User


class SignupForm(FlaskForm):
    first_name = StringField(validators=[DataRequired()])
    last_name = StringField(validators=[DataRequired()])
    email_address = EmailField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired(), Length(min=8)])

    def validate_email_address(self, field):
        email_exists = User.get_user_by_email(field.data)
        if email_exists:
            raise ValidationError("User with this email address already exists")

    def validate_password(self, field):
        basic_words = ["qwertyuiop", "password", "123456789", "security", "computer"]

        if field.data.lower() in basic_words:
            raise ValidationError("Enter a strong password.")


class LoginForm(FlaskForm):
    email_address = EmailField(validators=[DataRequired(), Email()])
    password = PasswordField(validators=[DataRequired()])

    def validate_email_address(self, field):
        user_exists = User.get_user_by_email(field.data)
        if not user_exists:
            print("testing")
            raise ValidationError(f"No user with email address: {field.data}")
