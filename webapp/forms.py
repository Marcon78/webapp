from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class CommentForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=255)],
                       render_kw={
                           "placeholder": "Your name",
                           "style": "background: url(/static/pics/login-locked-icon.png) no-repeat 5px center;text-indent: 28px"
                       })
    text = TextAreaField("Comment", validators=[DataRequired()])
    submit = SubmitField("Add Comment", render_kw={"style": "color:#FFFFFF; background-color:#337ab7"})
