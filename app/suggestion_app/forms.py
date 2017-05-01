"""
Defining forms for suggestion box application
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from app.models import Suggestion


class SuggestionBox(FlaskForm):
    """
    Form template for Suggestion box.
    """
    query = StringField('What would you like to know?')
    common = SelectField(
        'Frequent queries', coerce=int,
        choices=[(0, 'Select an query')]
                 + list(Suggestion.objects.values_list('id', 'query')))
    submit = SubmitField('Ask')
