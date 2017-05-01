"""
View controller for post app view.
"""
import datetime
from . import post_app, pa_logger
from .forms import PostForm, CommentForm
from app.models import Post, Tag, Comment
from flask_login import login_required, current_user
from flask import redirect, url_for, request, current_app, \
    render_template, abort, flash


@post_app.route('/', methods=['GET', 'POST'])
@post_app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data,
                    body_html=form.body_html.data,
                    author_id=current_user.id)
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
    qs = Post.objects().order_by('-timestamp')
    pagination = qs.paginate(page,
                             per_page=current_app.config['POSTS_PER_PAGE'],
                             error_out=False)
    posts = pagination.items
    pa_logger.info('Index page displaying {0} post items to user='
                   '{1}'.format(len(posts), current_user.id))
    return render_template('post/index.html', form=form, posts=posts,
                           pagination=pagination)


@post_app.route('/my_posts', methods=['GET', 'POST'])
@login_required
def my_posts():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data,
                    body_html=form.body_html.data,
                    author_id=current_user.id)
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
    qs = Post.objects(author_id=current_user.id).order_by('-timestamp')
    pagination = qs.paginate(page,
                             per_page=current_app.config['POSTS_PER_PAGE'],
                             error_out=False)
    posts = pagination.items
    pa_logger.info('Index page displaying {0} personal posts to user='
                   '{1}'.format(len(posts), current_user.id))
    return render_template('post/my_posts.html', form=form, posts=posts,
                           pagination=pagination)


@post_app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.objects(id=id).first_or_404()
    if current_user.id != post.author_id:
        pa_logger.warn('user={0} tried to edit inaccessible '
                       'post={1}'.format(current_user.id, post.id))
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
        return redirect(url_for('.post_page', id=post.id))
    form.body.data = post.body
    form.tags.data = ','.join([Tag.objects(id=i).first().text for i in
                               post.tags])
    return render_template('post/edit_post.html', form=form)


@post_app.route('/<int:id>', methods=['GET', 'POST'])
@login_required
def post_page(id):
    post = Post.objects(id=id).get_or_404()
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          commenter_id=current_user.id,
                          c_type=current_app.config["COMMENT_TYPE"]["POST"],
                          post_id=post.id)
        comment.save()
        flash('Your comment has been posted.')
        return redirect(url_for('.post_page', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (Comment.objects(
            c_type=current_app.config["COMMENT_TYPE"]["POST"],
            post_id=post.id).count() - 1) // \
               current_app.config['COMMENTS_PER_PAGE'] + 1
    qs = Comment.objects(
        c_type=current_app.config["COMMENT_TYPE"]["POST"],
        post_id=post.id).all().order_by('-timestamp')
    pagination = qs.paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return render_template('post/post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)


@post_app.route('/moderate/enable/<int:id>')
def moderate_enable(id):
    comment = Comment.objects.first_or_404(id)
    comment.disabled = False
    comment.save()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@post_app.route('/moderate/disable/<int:id>')
def moderate_disable(id):
    comment = Comment.objects.get_or_404(id)
    comment.disabled = True
    comment.save()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))
