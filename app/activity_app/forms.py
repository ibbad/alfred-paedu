"""
Forms templates for activity forms
"""

from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateTimeField
from wtforms import StringField, SubmitField
from wtforms import validators
from flask_pagedown.fields import PageDownField


class ActivityForm(FlaskForm):
    """
    Form template for activity_app.
    """
    title = StringField('Title', [validators.Required()])
    description = PageDownField('Description')
    tags = StringField('Tags')
    activity_time = DateTimeField('Time')
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    """
    Comments on activities.
    """
    body = PageDownField('Comment:')
    interested = SubmitField('Interested')
    going = SubmitField('Going')
    cancel = SubmitField('Cancel')
    submit = SubmitField('Submit')
