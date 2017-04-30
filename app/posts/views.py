"""
View controller for post app view.
"""
import datetime
from . import post_app, pa_logger
from .forms import PostForm, CommentForm
from app.models import Post, Tag, Comment
from flask import g, redirect, url_for, request, current_app, \
    render_template, abort, flash


@post_app.route('/', methods=['GET', 'POST'])
@post_app.route('/index', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data,
                    body_html=form.body_html.data,
                    author_id=g.current_user.id)
        tag_data = form.tags.data
        if tag_data != '':
            tags = [t.strip() for t in tag_data.split(',')]
            for tag in tags:
                if Tag.objects(text=tag).first() is not None:
                    post.tags.append(Tag.objects(text=tag).first().id)
                else:
                    t = Tag(text=tag).save()
                    post.tags.append(t.id)
                post.tags = list(set(post.tags))        # avoid repeated tags
        post.save()
        return redirect(url_for('.index'))

    page = request.args.get('page', 1, type=int)
    qs = Post.objects(author_id=g.current_user.id).order_by(
        'timestamp')
    pagination = qs.paginate(page,
                             per_page=current_app.config['POSTS_PER_PAGE'],
                             error_out=False)
    posts = pagination.items
    pa_logger('Index page displaying {0} post items to user='
                    '{1}'.format(len(posts), g.current_user.id))
    return render_template('post/index.html', form=form, posts=posts,
                           pagination=pagination)


@post_app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    post = Post.objects.first_or_404(id=id)
    if g.current_user.id != post.author_id:
        pa_logger.warn('user={0} tried to edit inaccessible '
                       'post={1}'.format(g.current_user.id, post.id))
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = post.body.data
        post.timestamp = datetime.utcnow()
        tag_data = form.tags.data
        if tag_data != '':
            tags = [t.strip() for t in tag_data.split(',')]
            for tag in tags:
                if Tag.objects(text=tag.strip()).first() is not None:
                    post.tags.append(Tag.objects(text=tag).first().id)
                else:
                    t = Tag(text=tag).save()
                    post.tags.append(t.id)
            post.tags = list(set(post.tags))            # avoid repeated tags
        post.save()
        flash('Post has been updated.')
    form.body.data = post.body
    form.tags.data = ','.join([Tag.objects(id=i).first() for i in post.tags])
    return render_template('post/edit_post.html', form=form)


@post_app.route('/<int:id>', methods=['GET', 'POST'])
def post_page(id):
    post = Post.objects.first_or_404(id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          commenter_id=g.current_user.id)
        comment.save()
        post.comments.append(comment.id)
        post.save()
        flash('Your comment has been posted.')
        return redirect(url_for('.post_page', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (len(post.comments) - 1) // current_app.config[
            'COMMENTS_PER_PAGE'] + 1
    qs = Comment.objects.filter(id in post.comments)
    pagination = qs.paginate(page,
                             per_page=current_app.config['POSTS_PER_PAGE'],
                             error_out=False)
    posts = pagination.items