"""
Templates for forms to be used in Post module
"""
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_pagedown.fields import PageDownField


class PostForm(Form):
    """
    Form template for submitting a post.
    """
    body = PageDownField("What's on your mind?", validators=[Required])
    tags = StringField("Tags")
    submit = SubmitField('Submit')


class CommentForm(Form):
    """
    Blueprint for submitting a comment.
    """
    body = StringField("Comment here:", validators=[Required])
    submit = SubmitField('Submit')
