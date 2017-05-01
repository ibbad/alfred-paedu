"""
View controller for suggestion box application
"""
from . import sugg_app, sa_logger
from .forms import SuggestionBox
from app.models import Suggestion
from flask_login import login_required
from flask import render_template, flash


@sugg_app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = SuggestionBox()
    # populate the common queries available in database already.
    form.common.choices = [(0, 'Select an query')] + list(
        Suggestion.objects.values_list('id', 'query'))
    if form.validate_on_submit():
        if form.query.data.strip():
            s = Suggestion.objects(
                query__icontains=form.query.data.strip()).first()
        elif form.common.data != 0:
            s = Suggestion.objects(id=form.common.data).first()
        else:
            flash('Please enter or choose a valid query.')
            return render_template('suggestion/suggestion_box.html', form=form)
        if s is None:
            flash('Unable to find related responses')
            sa_logger.info('Unable to find any responses for query='
                           '{0}'.format(form.query.data))
            return render_template('suggestion/suggestion_box.html',
                                   message='Unable to find matching '
                                           'responses',
                                   form=form)
        else:
            flash('Responses retrieved')
            print(s.responses)
            return render_template('suggestion/suggestion_box.html',
                                   responses=s.responses, form=form)
    return render_template('suggestion/suggestion_box.html', form=form)
