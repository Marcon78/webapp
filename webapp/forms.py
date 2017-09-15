from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

from webapp.models import User


class CommentForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=255)],
                       render_kw={
                           "placeholder": "Your name",
                           "style": "background: url(/static/pics/login-locked-icon.png) no-repeat 5px center;text-indent: 28px"
                       })
    text = TextAreaField("Comment", validators=[DataRequired()])
    submit = SubmitField("Add Comment", render_kw={"style": "color:#FFFFFF; background-color:#337ab7"})


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired, Length(1, 255)])
    password = PasswordField("Password", validators=[DataRequired])

    # validate 方法的实质就是依次调用每个成员属性的 validate_<fieldname> 方法。
    # 因此可以不用覆盖此方法，而是针对需要的处理的成员属性，编写 validate_<fieldname>
    def validate(self):
        check_validate = super(LoginForm, self).validate()

        if not check_validate:
            return False

        user = User.query.filter_by(username=self.username.data).first()
        if not user:
            self.username.errors.append("Invalid username or password.")
            return False

        if not user.check_password(self.password.data):
            self.username.errors.append("Invalid username or password.")
            return False

        return True