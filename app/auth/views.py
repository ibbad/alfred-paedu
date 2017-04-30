"""
Module for view functions for authentication module of webapp.
"""

from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, \
    current_user
from app.auth import auth_app, auth_logger
from app.auth.forms import LoginForm, ConfirmRegistrationForm, \
    ChangePasswordForm, PasswordResetRequestForm, ChangeEmailForm, \
    PasswordResetForm, ChangeLoginForm, ChangeUsernameForm
from app.models import User
from app.auth.authentication import login_exempt


@auth_app.before_request
def before_request():
    """
    To be executed before any request.
    :return:
    """
    if current_user.is_authenticated:
        # 3rd and 4th check to deal with infinite confirmation redirect request.
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth_webapp.' \
                and request.endpoint != 'static'\
                and request.endpoint[-11:] != 'unconfirmed'\
                and request.endpoint[-12:] != 'confirmation'\
                and request.endpoint[-7:] != 'confirm':
            auth_logger.warning('Unconfirmed users tried to make a request.')
            return redirect(url_for('auth_webapp.unconfirmed'))
    # FIXME: decide what to do for a user before request. something for
    # unconfirmed user
    pass


@auth_app.route('/unconfirmed')
@login_required
def unconfirmed():
    """
    View function for unconfirmed user.
    :return:
    """
    if not current_user.is_anonymous and current_user.confirmed:
        auth_logger.warning('Confirmed user %d tried to access a page '
                            'for confirmation.' % current_user.id)
        return redirect(url_for('user_app.index'))
    elif not current_user.is_anonymous:
        auth_logger.info('Unconfirmed user %d tried to access a page.' %
                         current_user.id)
        return render_template('auth/unconfirmed.html')
    else:
        return redirect(url_for('user_app.register'))


@auth_app.route('/login', methods=['GET', 'POST'])
def login():
    """
    View function for user login.
    :return:
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(email=form.username_or_email.data).first() or \
            User.objects(username=form.username_or_email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            auth_logger.info('User successfully logged in.')
            return redirect(request.args.get('next') or
                            url_for('user_app.index'))
        auth_logger.warning('Invalid credentials used for login.')
        flash('Invalid login credentials')
    return render_template('auth/login.html', form=form)


@auth_app.route('/logout')
@login_required
def logout():
    """
    View function for user logout.
    :return:
    """
    logout_user()
    auth_logger.info('User successfully logged out.')
    flash('You have been logged out.')
    return redirect(url_for('.login'))


@auth_app.route('/confirm/<conf_token>', methods=['GET', 'POST'])
@login_exempt
def confirm(conf_token):
    """
    View function for confirming a user using confirmation token.
    :param conf_token:
    :return:
    """
    form = ConfirmRegistrationForm()
    if form.validate_on_submit():
        user = User.verify_confirmation_token(conf_token)
        if user is not None:
            auth_logger.info('User %d successfully confirmed using '
                             'confirmation token.' % user.id)
            flash('Your account has been confirmed.')
            return redirect(url_for('user_app.edit_profile'))
        else:
            auth_logger.warning(
                'Invalid confirmation token used for confirmation.')
            flash('The confirmation token is either invalid or expired.')
            return redirect(url_for('auth_webapp.login'))
    return render_template('auth/auth_confirm.html', form=form)


@auth_app.route('/confirm')
@login_required
def resend_confirmation():
    """
    View function for requesting a confirmation token for the user.
    :return:
    """
    conf_token = current_user.generate_confirmation_token()
    auth_logger.info('Confirmation token successfully generated for the '
                     'user.')
    flash('Redirecting to confirmation page.')
    return redirect(url_for('auth_webapp.confirm', conf_token=conf_token))


@auth_app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    View function for changing user's password.
    :return:
    """
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.set_password(form.password.data)
            current_user.save()
            auth_logger.info('User password updated successfully.')
            logout_user()
            flash('Your password has been changed, please login to continue.')
            return redirect(url_for('.login'))
        else:
            auth_logger.warning('Invalid password used to login for changing '
                                'password.')
            flash('Invalid password.')
    return render_template('auth/change_password.html', form=form)


@auth_app.route('/rqst_pwd_reset', methods=['GET', 'POST'])
def password_reset_request():
    """
    View function for requesting to generate a reset password token. Using
    this token user will be able to change its forgotten password.
    :return:
    """
    if not current_user.is_anonymous:
        return redirect(url_for('user_app.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.objects(email=form.username_or_email.data).first() or \
            User.objects(username=form.username_or_email.data).first()
        if not user:
            auth_logger.warning('Request to change password for non existing '
                                'user.')
            flash('User with given username or email address does '
                  'not exist.')
            return redirect(url_for('.password_reset_request'))
        pwd_rst_token = user.generate_pwd_reset_token()
        auth_logger.info('Password reset token successfully generated for '
                         'user: %s' % user.username)
        flash('Redirecting to password reset page.')
        auth_logger.info('User redirected to page for resetting password')
        return redirect(url_for('.password_reset',
                                password_reset_token=pwd_rst_token))
    return render_template('auth/reset_password.html', form=form)


@auth_app.route('/reset_password/<password_reset_token>',
                   methods=['GET', 'POST'])
def password_reset(password_reset_token):
    """
    View function to verify the password reset token and change the
    user's password.
    :param password_reset_token: Password reset token issued to the user.
    :return:
    """
    if not current_user.is_anonymous:
        auth_logger.warning('Attempt to change password for anonymous '
                            'user blocked.')
        return redirect(url_for('user_app.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.verify_pwd_reset_token(
            pwd_reset_token=password_reset_token)
        if user is None:
            auth_logger.warning('Invalid password reset token used for '
                                'changing password.')
            flash('No user registered with given '
                  'username or email address.')
            return redirect(url_for('user_app.index'))
        if user.change_password(password_reset_token, form.password.data):
            auth_logger.info('User: %s password sucessfully updated.' %
                             user.username)
            flash('Password has been updated.')
            return redirect(url_for('.login'))
        else:
            auth_logger.warning('Unable to update password for User: %s' %
                                user.username)
            return redirect(url_for('user_app.index'))
    return render_template('auth/reset_password.html', form=form)


@auth_app.route('/change_login', methods=['GET', 'POST'])
@login_required
def change_login_request():
    """
    View function for the request to generate the login change token for the
    user. Using this token a user will be able to change its
    login information i.e. username or email address.
    :return:
    """
    form = ChangeLoginForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            login_change_token = current_user.generate_login_change_token(
                username_or_email=form.username_or_email.data)
            auth_logger.info('user login successfully updated for %s'
                             % current_user.username)
            flash('Your login credentials are being changed.')
            return redirect(url_for('.change_login',
                                    login_change_token=login_change_token))
        auth_logger.warning('Invalid password used to change login '
                            'credentials for User: %s'
                            % current_user.username)
        flash('Invalid login credentials.')
    return render_template('auth/change_login.html', form=form)


@auth_app.route('/change_login_username', methods=['GET', 'POST'])
@login_required
def change_username_request():
    """
    View function for a request to change username of the user.
    :return:
    """
    form = ChangeUsernameForm(new_username=current_user.username)
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            login_change_token = current_user.generate_login_change_token(
                username_or_email=form.new_username.data)
            auth_logger.info('Username change token successfully '
                             'generated for User: %s' %
                             current_user.username)
            flash('Your username is being changed.')
            return redirect(url_for('.change_login',
                                    login_change_token=login_change_token))
        auth_logger.warning('Invalid password used to request username change '
                            'token for User: %s' %
                            current_user.username)
        flash('Invalid password.')
    return render_template('auth/change_username.html', form=form)


@auth_app.route('/change_login_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    """
    View function for a request to change email address of the user.
    :return:
    """
    form = ChangeEmailForm(new_email=current_user.email)
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            login_change_token = current_user.generate_login_change_token(
                username_or_email=form.new_email.data)
            auth_logger.info('Email change token successfully '
                             'generated for User: %s' %
                             current_user.username)
            flash('Your email address is being changed.')
            return redirect(url_for('.change_login',
                                    login_change_token=login_change_token))
        auth_logger.warning('Invalid password used to request email change '
                            'token for User: %s' %
                            current_user.username)
        flash('Invalid password.')
    return render_template('auth/change_email.html', form=form)


@auth_app.route('/change_login/<login_change_token>')
@login_required
def change_login(login_change_token):
    """
    View function to request change of login information using the token
    generated for the user in a previous call.
    :param login_change_token: Token generated for the user upon
    request for login change.
    :return:
    """
    if current_user.change_login(login_change_token):
        auth_logger.info('Login credentials successfully updated for '
                         'User: %s' % current_user.username)
        logout_user()
        flash('Your login information has been updated, '
              'please login to continue.')
        return redirect(url_for('.login'))
    else:
        auth_logger.error('Unable to change login credentials for User: '
                          '%s' % current_user.username)
    return redirect(url_for('user_app.index'))
