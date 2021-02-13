from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, HiddenField, validators, SubmitField

from sqlbase import Comment


class CommentForm(FlaskForm):
    pseudonym = StringField("Pseudonym", [validators.DataRequired(), validators.Length(max=32)])
    comment = TextAreaField("Comment", [validators.DataRequired(), validators.Length(max=8192)])
    hidden_password = HiddenField("Hidden Password", [validators.Length(min=32, max=32)])
    submit = SubmitField("Post Public Comment")

    def to_database_object(self) -> any:
        return Comment(self.pseudonym.data, self.hidden_password.data, self.comment.data)
