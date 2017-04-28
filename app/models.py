import hashlib
import random
from datetime import datetime, timedelta
from mongoengine import ValidationError
from mongoengine.queryset import NotUniqueError
from flask import current_app, request, url_for
from flask.ext.login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, \
    BadSignature, SignatureExpired
from app import db, login_manager
from app.IPProtocol import IPProtocol
from helper.CONSTANTS import EMAIL_REGEX
from helper.helper_functions import isEmail, mac2int, int2mac, ip2int, int2ip, \
    generate_random_mac, generate_random_ip, isvalidIP


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

# When user is not logged in, he/she is assigned an anonymous user.
login_manager.anonymous_user = AnonymousUser


class Permission:
    """
    Different individual and set of permissions assigned to users for
    performing different operations.
    """
    PERM_NONE = 0x000
    PERM_STUDENT = 0x001
    PERM_PARENTS = 0x002
    PERM_TEACHER = 0x004
    PERM_ADMIN = 0xfff    # All permissions

    def __init__(self):
        pass

class Address(db.EmbeddedDocument):
    """
    Address sub-document for storing address of each user.
    Address is comprised of:
    1. street address (house+building address)
    2. City
    3. Postal/Zip code
    4. State
    5. Country
    """

    # TODO: Re-evaluate the requirements for storing address sub fields.

    # FIXME: Add required=True for respective fields.
    street = db.StringField(max_length=255)
    city = db.StringField(max_length=64)
    postalcode = db.StringField(max_length=20)
    state = db.StringField(max_length=50)
    country = db.StringField(max_length=20)

    def to_json(self):
        json_address = {
            "street": self.street,
            "city": self.city,
            "postalcode": self.postalcode,
            "state": self.state,
            "country": self.country,
        }
        return json_address

    @staticmethod
    def from_json(json_address):
        return Address(
            street=json_address.get('street') or '',
            city=json_address.get('city') or '',
            postalcode=json_address.get('postalcode') or '',
            state=json_address.get('state') or '',
            country=json_address.get('country') or '',
        )

    def __repr__(self):
        return '<Address: %s>' % self.street+', '+self.postalcode+', ' + \
               self.city+', '+self.country


class Wallpost(db.Document):
	__collectionname__ = 'wallpost'
	id = db.SequenceField(primary_key=True)
	body = db.StringField()
	body_html = db.StringField()
	timestamp = db.DateTimeField(default=datetime.utcnow())
	author_id = db.IntField(min_value=1)
	comments = db.ListField(db.StringField())
	tags = db.ListField(db.StringField())

class WallpostComment(db.Document):
	__collectionname__ = 'WallpostComments'
	id = db.SequenceField(primary_key=True)
	body = db.StringField()
	body_html = db.StringField()
	timestamp = db.DateTimeField(default=datetime.utcnow())
	commenter_id = db.IntField(min_value=1)
	wallpost_id = db.IntField(min_value=1)

class Diary(db.Document):
	__collectionname__ = 'diary'
	id = db.SequenceField(primary_key=True)
	body = db.StringField()
	body_html = db.StringField()
	timestamp = db.DateTimeField(default=datetime.utcnow())
	author_id = db.IntField(min_value=1)
	tags = db.ListField(db.StringField())
	# No comments for personal diary

class Activity(db.Document):
	__collectionname__ = 'activity'
	id = db.SequenceField(primary_key=True)
	body = db.StringField()
	body_html = db.StringField()
	timestamp = db.StringField()
	tags= db.ListField(db.StringField())
	interested = db.ListField(db.IntField(min_value=1))
	going = db.ListField(db.IntField(min_value=1))

class User(UserMixin, db.Document):
    """
    User document structure.
    """
    # FIXME: Decide a schema and move to Document instead of Dynamic document.
    __collectionname__ = 'subscriber'
    id = db.SequenceField(primary_key=True)
    # FIXME: ensure uniqueness of email and username in business logic.
    email = db.EmailField(regex=EMAIL_REGEX, max_length=64, required=True,
                          unique=True)
    username = db.StringField(regex=USERNAME_REGEX, max_length=64,
                              required=True, unique=True)
    password_hash = db.StringField(max_length=128)
    confirmed = db.BooleanField(default=False)
    avatar_hash = db.StringField(max_length=32)
    permissions = db.IntField(default=None)

    # User information
    # FIXME: Remove extra fields
    first_name = db.StringField(max_length=64)
    last_name = db.StringField(max_length=64)
    phone = db.StringField(max_length=20)
    company = db.StringField(max_length=64)
    address = db.EmbeddedDocumentField(document_type=Address)
    joined = db.DateTimeField(default=datetime.utcnow())

    # Relations 
    parents = db.ListField(db.IntField(min_value=1), default=[])
    friends = db.ListField(db.IntField(min_value=1), default=[])
    teachers = db.ListField(db.IntField(min_value=1), default=[])

    # Define indexes
    # FIXME: Check the tradeoff between hashed and plain-text indexes.
    # FIXME: remove sparse indexes in production deployment.
    meta = {
        'allow-inheritance': True,
        'index-background': True,
        'sparse': True,
        'ordering': ['joined'],
    }

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.permissions is None:
            if self.email == current_app.config['APP_ADMIN']:
                self.permissions = Permission.admin_permissions
            if self.permissions is None:
                self.permissions = Permission.user_permissions
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8'))\
                                      .hexdigest()

    def set_password(self, password):
        """
        Generate and store password hash for the subscriber.
        :param password: user provided password.
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Verify user password against the hash stored in database.
        :param password: user password.
        :return: True if verified else False.
        """
        return check_password_hash(self.password_hash, password)

    def can(self, permission):
        """
        Returns if a subscriber has enough permission to perform an operation.
        :param permission: Permission name.
        :return: True if subscriber has a permission.
        """
        return (self.permissions & permission) == permission

    def generate_auth_token(self, expiration=3600):
        """
        Generate authentication token for token-based user authentication.
        :param expiration: expiry of token.
        :return: authentication token.
        """
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        """
        Verify the authentication token generated for the user authentication.
        :param token: authentication token.
        :return: User object if token is valid/not-expired.
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except (SignatureExpired, BadSignature):
            return None
        return User.objects(id=data['id']).first()

    def generate_pwd_reset_token(self, expiration=3600):
        """
        Generates a password reset token for the user.
        :param expiration: validity for the token (default=3600sec).
        :return: password reset token.
        """
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'reset': self.id})

    @staticmethod
    def verify_pwd_reset_token(pwd_reset_token):
        """
        Verify the authentication token generated for the resting password.
        :param pwd_reset_token: password reset token.
        :return: User object if token is valid/not-expired.
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(pwd_reset_token)
        except (SignatureExpired, BadSignature):
            return None
        return User.objects(id=data['reset']).first()

    def change_password(self, pwd_reset_token, new_password):
        """
        Replaces user current password with user provided password.
        :param pwd_reset_token: Reset token generated for the user.
        :param new_password: New password provided by the user.
        :return: True if successful, False otherwise.
                 None if token is bad/expired.
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(pwd_reset_token)
        except (SignatureExpired, BadSignature):
            return None
        if data.get('reset') != self.id:
            return False
        self.set_password(new_password)
        self.save()
        return True

    def generate_confirmation_token(self, expiration=7200):
        """
        Generates a account confirmation token for the user.`
        :return: account confirmation token.
        """
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, confirmation_token):
        """
        Checks the user account confirmation token and confirms the account.
        :param confirmation_token: Account information token for the user.
        :return: True if successful, False otherwise.
                 None if token is bad/expired.
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(confirmation_token)
        except (SignatureExpired, BadSignature):
            return None
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        self.save()
        return True

    @staticmethod
    def verify_confirmation_token(confirmation_token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(confirmation_token)
        except (SignatureExpired, BadSignature):
            return None
        sub = User.objects(id=data.get('confirm')).first()
        if sub is not None:
            sub.confirmed = True
            sub.save()
            return sub
        return None

    def generate_login_change_token(self, username_or_email, expiration=3600):
        """
        Generates a new token for changing login information (i.e. username,
        email address) of valid subscriber. This token contains the changed
        username/email information of subscriber and using this token will
        change the username/email address in the database.
        :param username_or_email: new login information i.e.
        username/email address.
        :param expiration: expiry time of token (default=3600).
        :return:
        """
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'change_login': self.id,
                        'new_login': username_or_email})

    def change_login(self, login_change_token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(login_change_token)
        except (SignatureExpired, BadSignature):
            return None
        if data.get('change_login') != self.id or data.get('new_login') is None:
            return False
        new_login = data.get('new_login')
        if isEmail(new_login):
            if User.objects(email=new_login).first() is not None:
                # new email already exists
                return False
            self.email = new_login
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        else:
            if User.objects(username=new_login).first() is not None:
                # new username already exists.
                return False
            self.username = new_login
        self.save()
        return True

    def gravatar(self, size=100, default='identicon', rating='g'):
        """
        Generates an avatar for profile picture.
        :param size: size of image (default=100).
        :param default: default style for avatar icon.
        :param rating: rating for avatar icon.
        :return: url for subscriber's avatar icon.
        """
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'

        hash = self.avatar_hash or \
            hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def to_json(self):
        """
        Gives a json representation of the subscriber.
        :return: json representation of subscriber document.
        """
        json_subscriber = {
            'url': url_for('api.get_subscriber', sub_id=self.id,
                           _external=True),
            'username': self.username,
            'name': '%s %s' % (self.first_name, self.last_name),
            'address': self.address.to_json() if self.address else '',
            'company': self.company,
            'phone': self.phone,
            'email': self.email,
        }
        return json_subscriber

    @staticmethod
    def from_json(json_data):
        """
        Register a new subscriber document from the json data.
        :return: User object that is created from json data.
        """
        subscriber = User(username=json_data.get('username'),
                                email=json_data.get('email'))
        if json_data.get('password') is None:
            return None
        subscriber.set_password(json_data.get('password'))
        if json_data.get('name') is not None:
            subscriber.first_name = json_data.get('name')['first'] or ''
            subscriber.last_name = json_data.get('name')['last'] or ''
        subscriber.company = json_data.get('company') or ''
        subscriber.phone = json_data.get('phone') or ''
        subscriber.address = Address.from_json(json_data.get('address')) \
            if json_data.get('address') \
            else None
        return subscriber

    def update_from_json(self, json_data):
        """
        Update the subscriber document from json data.
        Note: username, email and password must be changed using tokens only.
        """
        if json_data.get('name') is not None:
            self.first_name = json_data.get('name')['first'] or self.first_name
            self.last_name = json_data.get('name')['last'] or self.last_name
        self.company = json_data.get('company') or self.company
        self.phone = json_data.get('phone') or self.phone
        if json_data.get('address') is not None:
            self.address = Address.from_json(json_data.get('address'))
        self.save()

    def __repr__(self):
        return '<User %r>' % self.username

    @staticmethod
    def generate_fake(fakes_required=100):
        """
        Generates fake subscribers and store them in the database.
        :param fakes_required: Number of fakes to generate
        :return:
        """
        from mongoengine import ValidationError
        from random import seed
        import forgery_py

        seed()
        fakes = 0
        while fakes < fakes_required:
            try:
                usr = User(
                    username=forgery_py.internet.user_name(with_num=True),
                    email=forgery_py.internet.email_address(),
                    first_name=forgery_py.name.first_name(),
                    last_name=forgery_py.name.last_name(),
                    confirmed=True,
                    phone=forgery_py.address.phone(),
                    company=forgery_py.lorem_ipsum.word()
                )

                address = Address(
                    street=forgery_py.address.street_address(),
                    city=forgery_py.address.city(),
                    postalcode=forgery_py.address.zip_code(),
                    country=forgery_py.address.country()
                )
                usr.address = address
                usr.confirmed = True
                usr.set_password('password')
                usr.save()
                fakes += 1
            except ValidationError:
                pass
            except Exception:
                pass


@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=int(user_id)).first()