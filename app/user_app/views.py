"""
View functions for user webapp v1.0
"""
from flask import render_template, redirect, url_for, abort, flash, request, \
    current_app
from flask.ext.login import login_required, current_user
from app.user_app import user_app, user_app_logger
from app.user_app.forms import EditProfileForm, RegistrationForm
from app.models import User, Address, Permission
from helper.countries import countries, get_country_key


@user_app.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@user_app.route('/register', methods=['GET', 'POST'])
def register():
    """
    View function for a registering a new user.
    :return:
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                         email=form.email.data)
        user.set_password(form.password.data)
        user.save()
        # TODO: generate and send confirmation token for the user.
        conf_token = user.generate_confirmation_token()
        user_app_logger.info('Confirmation token successfully generated for '
                             'user.')
        flash('Registration successful.')
        return redirect(url_for('auth_webapp.confirm', conf_token=conf_token))
    return render_template('user/register.html', form=form)


@user_app.route('/')
@user_app.route('/index')
def index():
    """
    View function to return the index page for the user request.
    :return:
    """
    if current_user.is_anonymous:
        user_app_logger.info('Serving index page to anonymous user.')
        return render_template('index.html')
    """
    Show top 5 securebox and top 10 devices in the order of decreasing data
    usage.
    """
    device_list = Device.objects(registered_to=current_user.id)\
                        .order_by('-data_used')\
                        .all()
    user_app_logger.debug('Device list with %d devices registered to '
                          'user %d retrieved to display on index page/ '
                          % (len(device_list), current_user.id))

    sbox_list = Securebox.objects(registered_to=current_user.id).all()
    user_app_logger.debug('sbox list with %d devices registered to '
                          'user %d retrieved to display on index page/ '
                          % (len(sbox_list), current_user.id))

    user_app_logger.info('Index page displayed to user %d with %d '
                         'devices and %d secureboxes ' %
                         (current_user.id, len(device_list), len(sbox_list)))
    return render_template('user/user_index.html',
                           device_list=device_list,
                           sbox_list=sbox_list)


@user_app.route('/profile/<username_or_email>')
@login_required
def profile_page(username_or_email):
    """
    This view function takes the username/email address of the user
    and returns the profile page of user.
    :param username_or_email: Username or email address of the user
    whose profile page is accessed.
    :return:
    """
    user = User.objects(username=username_or_email).first() or \
        User.objects(username=username_or_email).first()
    if user is None:
        user_app_logger.warning('User %d request for info page of '
                                'non existing user %s' % (current_user.id,
                                                          username_or_email))
        return render_template('errors/404.html')
    """
    If the logged in user is trying to access some other user's
    profile, minimal information is presented.
    """
    if user.id != current_user.id and \
        User.objects(id=current_user.id).first().permissions != \
            Permission.PERM_ADMIN:
        user_app_logger.info('Displaying user %d profile page for '
                             'user %d' % (user.id, current_user.id))
        return render_template('user/user_profile_minimal.html',
                               user=user)
    # Full information is provided to the user for his own profile view.
    user_app_logger.info('displaying profile page with full information to '
                         'user %d' % user.id)
    return render_template('user/profile.html', user=user)


@user_app.route('/profile/<int:user_id>')
def profile_page_id(user_id):
    """
    This view function takes the IDof the user and returns the profile
    page of the respective user.
    :param user_id: ID of the user
    whose profile page is accessed.
    :return:
    """
    user = User.objects(id=user_id).first()
    if user is None:
        user_app_logger.error('User %d requested profile page for non'
                              ' existing user %d' % (current_user.id, user_id))
        return render_template('errors/404.html')
    """
    If the logged in user is trying to access some other user's
    profile, minimal information is presented.
    """
    if user.id != current_user.id and \
        User.objects(id=current_user.id).first().permissions != \
            Permission.PERM_ADMIN:
        user_app_logger.info('Displaying user %d profile page for '
                             'user %d' % (user.id, current_user.id))
        return render_template('user/user_profile_minimal.html',
                               user=user)
    # Full information is provided to the user for his own profile view..
    user_app_logger.info('displaying profile page with full information to '
                         'user %d' % user.id)
    return render_template('user/profile.html', user=user)


@user_app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    This view function presents the page edit information about the user.
    :return:
    """
    form = EditProfileForm(
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        company=current_user.company,
        phone=current_user.phone,
        country=get_country_key(current_user.address.country) if
        current_user.address else None)
    user_app_logger.debug('edit profile form populated for user %d' %
                            current_user.id)
    if form.validate_on_submit():
        user_app_logger.debug('edit profile form submitted by user '
                                '%d' % current_user.id)
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.company = form.company.data
        current_user.phone = form.phone.data
        # If there is no address previously, create address object.
        if current_user.address is None:
            user_app_logger.debug('No address previously registered to '
                                  'user %d' % current_user.id)
            current_user.address = Address()
        current_user.address.street = form.street.data
        current_user.address.postalcode = form.postalcode.data
        current_user.address.city = form.city.data
        current_user.address.state = form.state.data
        current_user.address.country = countries.get(form.country.data)
        current_user.save()
        user_app_logger.info('user %d profile updated successfully' %
                             current_user.id)
        flash('Profile information has been updated.')
        user_app_logger.debug('user %d being redirected to profile '
                              'page after profile update' % current_user.id)
        return redirect(url_for('user_app.profile_page',
                                username_or_email=current_user.username))
    # Populate the form for GET request.
    if current_user.address is not None:
        form.street.data = current_user.address.street or ''
        form.postalcode.data = current_user.address.postalcode or ''
        form.city.data = current_user.address.city or ''
        form.state.data = current_user.address.state or ''
    user_app_logger.info('Edit profile form being displayed to user '
                         '%d' % current_user.id)
    return render_template('user/edit_profile.html', form=form)