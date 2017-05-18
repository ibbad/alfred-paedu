"""
Forms templates for Diary forms
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms import validators
from flask_pagedown.fields import PageDownField


class DiaryForm(FlaskForm):
    """
    Form template for diary.
    """
    title = StringField('Title', [validators.Required()])
    description = PageDownField('Description', [validators.Required()])
    tags = StringField('Tags')
    s_activity = StringField('Study activities')
    s_time = FloatField('Hours')
    o_activity = StringField('Other activities')
    o_time = FloatField('Hours')
    submit = SubmitField('Submit')
