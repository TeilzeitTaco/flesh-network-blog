from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, HiddenField, validators, SubmitField

from sqlbase import Comment


class CommentForm(FlaskForm):
    pseudonym = StringField("Pseudonym", [validators.Length(min=1, max=32)])
    comment = TextAreaField("Comment", [validators.Length(min=3, max=8192)])

    # This is required so we can verify the identity of the submitter without
    # requiring an explicit account. It gets filled in from localStorage using javascript.
    hidden_password = HiddenField("Hidden Password", [validators.Length(min=32, max=32)])

    submit = SubmitField("Post Public Comment")

    def to_database_object(self) -> any:
        return Comment(self.pseudonym.data, self.hidden_password.data, self.comment.data)
