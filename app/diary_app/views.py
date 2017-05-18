"""
View controller for diary app views.
"""
from datetime import datetime
from . import diary_app, da_logger
from .forms import DiaryForm
from app.models import Diary, Tag
from flask_login import login_required, current_user
from flask import redirect, url_for, request, current_app, render_template, \
    abort, flash


@diary_app.route('/', methods=['GET', 'POST'])
@diary_app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    qs = Diary.objects(author_id=current_user.id).order_by('-timestamp')
    pagination = qs.paginate(page,
                             per_page=current_app.config["DIARIES_PER_PAGE"],
                             error_out=False)
    diaries = pagination.items
    return render_template('diary/index.html', diaries=diaries,
                           pagination=pagination)


@diary_app.route('/<int:d_id>', methods=['GET'])
@login_required
def diary_page(d_id):
    d = Diary.objects(id=d_id).get_or_404()
    if d.author_id != current_user.id:
        da_logger.warn('user={0} tried to edit inaccessible '
                       'diary={1}'.format(current_user.id, d.id))
        abort(403)
    return render_template('diary/diary.html', diary=d)


@diary_app.route('/edit/<int:d_id>', methods=['GET', 'POST'])
@login_required
def edit_diary(d_id):
    d = Diary.objects(id=d_id).get_or_404()
    if d is not None and d.author_id != current_user.id:
        da_logger.warn('user={0} tried to edit inaccessible '
                       'diary={1}'.format(current_user.id, d.id))
        abort(403)
    form = DiaryForm()
    if form.validate_on_submit():
        d.title = form.title.data
        d.description = form.description.data
        d.timestamp = datetime.utcnow()
        d.s_activity = [s_a.strip() for s_a in form.s_activity.data.split(',')]
        d.s_time = form.s_time.data
        d.o_activity = [o_a.strip() for o_a in form.o_activity.data.split(',')]
        d.o_time = form.o_time.data
        tag_data = form.tags.data
        if tag_data != '':
            tags = [t.strip() for t in tag_data.split(',')]
            for tag in tags:
                if Tag.objects(text=tag.strip()).first() is not None:
                    d.tags.append(Tag.objects(text=tag).first().id)
                else:
                    t = Tag(text=tag).save()
                    d.tags.append(t.id)
            d.tags = list(set(d.tags))               # avoid repeated tags
        d.author_id = current_user.id
        d.save()
        flash('Diary is updated')
        return redirect(url_for('.diary_page', d_id=d.id))
    form.title.data = d.title
    form.description.data = d.description
    form.s_activity.data = ','.join([s_a for s_a in d.s_activity])
    form.s_time.data = d.s_time
    form.o_activity.data = ','.join([o_a for o_a in d.o_activity])
    form.o_time.data = d.o_time
    form.tags.data = ','.join([Tag.objects(id=i).first().text
                               for i in d.tags])
    return render_template('diary/edit_diary.html', form=form)


@diary_app.route('/add', methods=['GET', 'POST'])
@login_required
def add_diary():
    form = DiaryForm()
    if form.validate_on_submit():
        d = Diary()
        d.title = form.title.data
        d.description = form.description.data
        d.timestamp = datetime.utcnow()
        d.s_activity = [s_a.strip() for s_a in form.s_activity.data.split(',')]
        d.s_time = form.s_time.data
        d.o_activity = [o_a.strip() for o_a in form.o_activity.data.split(',')]
        d.o_time = form.o_time.data
        tag_data = form.tags.data
        if tag_data != '':
            tags = [t.strip() for t in tag_data.split(',')]
            for tag in tags:
                if Tag.objects(text=tag.strip()).first() is not None:
                    d.tags.append(Tag.objects(text=tag).first().id)
                else:
                    t = Tag(text=tag).save()
                    d.tags.append(t.id)
            d.tags = list(set(d.tags))            # avoid repeated tags
        d.author_id = current_user.id
        d.save()
        flash('Diary is updated')
        return redirect(url_for('.diary_page', d_id=d.id))
    form.o_time.data = 0
    form.s_time.data = 0
    return render_template('diary/add_diary.html', form=form)
