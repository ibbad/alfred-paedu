"""
Forms templates for Diary forms
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms import validators
from flask_pagedown.fields import PageDownField


class DiaryForm(FlaskForm):
    """
    Form template for diary.
    """
    title = StringField('Title', [validators.Required()])
    description = PageDownField('Description')
    tags = StringField('Tags')
    s_activity = StringField('Study activities')
    s_time = IntegerField('Hours')
    o_activity = StringField('Other activities')
    o_time = IntegerField('Hours')

