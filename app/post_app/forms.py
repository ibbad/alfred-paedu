"""
Templates for forms to be used in Post module
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms import validators
from flask_pagedown.fields import PageDownField


class PostForm(FlaskForm):
    """
    Form template for submitting a post.
    """
    body = PageDownField("What's on your mind?", [validators.Required()])
    tags = StringField("Tags")
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    """
    Blueprint for submitting a comment.
    """
    body = PageDownField("Comment here:", [validators.Required()])
    submit = SubmitField('Submit')
