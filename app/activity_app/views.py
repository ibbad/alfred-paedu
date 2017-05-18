"""
View controller for post app view.
"""
from datetime import datetime
from . import activity_app, aa_logger
from .forms import ActivityForm, CommentForm
from app.models import Activity, Tag, Comment
from flask_login import login_required, current_user
from flask import redirect, url_for, request, current_app, \
    render_template, abort, flash


@activity_app.route('/', methods=['GET', 'POST'])
@activity_app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    qs = Activity.objects().order_by('-timestamp')
    pagination = qs.paginate(page,
                             per_page=current_app.config['POSTS_PER_PAGE'],
                             error_out=False)
    activities = pagination.items
    aa_logger.info('Index page displaying {0} activity items to user='
                   '{1}'.format(len(activities), current_user.id))
    return render_template('activity/index.html', activities=activities,
                           pagination=pagination)


@activity_app.route('/add', methods=['GET', 'POST'])
@login_required
def add_activity():
    form = ActivityForm()
    if form.validate_on_submit():
        a = Activity()
        a.title = form.title.data
        a.description = form.description.data
        a.timestamp = datetime.utcnow()
        a.activity_time = form.activity_time.data
        tag_data = form.tags.data
        if tag_data != '':
            tags = [t.strip() for t in tag_data.split(',')]
            for tag in tags:
                if Tag.objects(text=tag.strip()).first() is not None:
                    a.tags.append(Tag.objects(text=tag).first().id)
                else:
                    t = Tag(text=tag).save()
                    a.tags.append(t.id)
            a.tags = list(set(a.tags))            # avoid repeated tags
        a.author_id = current_user.id
        a.save()
        flash('Activity is updated')
        return redirect(url_for('.activity_page', a_id=a.id))
    form.activity_time.data = datetime.utcnow()
    return render_template('activity/add_activity.html', form=form)


@activity_app.route('/edit/<int:a_id>', methods=['GET', 'POST'])
@login_required
def edit_activity(a_id):
    a = Activity.objects(id=a_id).get_or_404()
    if a is not None and a.author_id != current_user.id:
        aa_logger.warn('user={0} tried to edit inaccessible '
                       'activity={1}'.format(current_user.id, a.id))
        abort(403)
    form = ActivityForm()
    if form.validate_on_submit():
        a.description = form.description.data
        a.timestamp = datetime.utcnow()
        a.activity_time = form.activity_time.data
        tag_data = form.tags.data
        if tag_data != '':
            tags = [t.strip() for t in tag_data.split(',')]
            for tag in tags:
                if Tag.objects(text=tag.strip()).first() is not None:
                    a.tags.append(Tag.objects(text=tag).first().id)
                else:
                    t = Tag(text=tag).save()
                    a.tags.append(t.id)
            a.tags = list(set(a.tags))               # avoid repeated tags
        a.author_id = current_user.id
        a.save()
        flash('Activity is updated')
        return redirect(url_for('.activity_page', a_id=a.id))
    form.title.data = a.title
    form.description.data = a.description
    form.activity_time.data = a.activity_time
    form.tags.data = ','.join([Tag.objects(id=i).first().text
                               for i in a.tags])
    return render_template('activity/edit_activity.html', form=form)


@activity_app.route('/<int:a_id>', methods=['GET', 'POST'])
@login_required
def activity_page(a_id):
    print('%' * 80)
    print(a_id)
    print('%' * 80)
    a = Activity.objects(id=a_id).get_or_404()
    cf = CommentForm()
    if cf.validate_on_submit():
        if cf.interested.data:
            if current_user.id not in a.interested:
                a.interested.append(current_user.id)
            a.save()
            flash('You interested in noted')
        elif cf.going.data:
            if current_user.id not in a.going:
                a.going.append(current_user.id)
            if current_user.id in a.interested:
                a.interested.remove(current_user.id)
            a.save()
            flash('You are marked as going')
        elif cf.cancel.data:
            if current_user in a.going:
                a.going.remove(current_user.id)
            if current_user in a.interested:
                a.interested.remove(current_user.id)
            a.save()
            flash('Your interest has been removed')
        elif cf.body.data:
            comment = Comment(body=cf.body.data,
                              commenter_id=current_user.id,
                              c_type=current_app.config["COMMENT_TYPE"][
                                  "ACTIVITY"],
                              post_id=a.id)
            comment.save()
            flash('Your comment has been posted.')
        return redirect(url_for('.activity_page', a_id=a.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (Comment.objects(
            c_type=current_app.config["COMMENT_TYPE"]["ACTIVITY"],
            post_id=a.id).count() - 1) // \
               current_app.config['COMMENTS_PER_PAGE'] + 1
    qs = Comment.objects(
        c_type=current_app.config["COMMENT_TYPE"]["ACTIVITY"],
        post_id=a.id).all().order_by('-timestamp')
    pagination = qs.paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return render_template('activity/activity.html', activity=a, form=cf,
                           comments=comments, pagination=pagination)


@activity_app.route('/my_activities', methods=['GET', 'POST'])
@login_required
def my_activities():
    page = request.args.get('page', 1, type=int)
    qs = Activity.objects(author_id=current_user.id).order_by('-timestamp')
    pagination = qs.paginate(page,
                             per_page=current_app.config['POSTS_PER_PAGE'],
                             error_out=False)
    activities = pagination.items
    aa_logger.info('Index page displaying {0} personal posts to user='
                   '{1}'.format(len(activities), current_user.id))
    return render_template('activity/my_activities.html',
                           activities=activities,
                           pagination=pagination)


@activity_app.route('/moderate/enable/<int:id>')
def moderate_enable(id):
    comment = Comment.objects.first_or_404(id)
    comment.disabled = False
    comment.save()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@activity_app.route('/moderate/disable/<int:id>')
def moderate_disable(id):
    comment = Comment.objects.get_or_404(id)
    comment.disabled = True
    comment.save()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))
