"""
Module containing blueprints for application models.
"""

import random
import hashlib
import logging
import forgery_py
from datetime import datetime, timedelta
from mongoengine import ValidationError
from mongoengine.queryset import NotUniqueError
from flask import current_app, request, url_for, jsonify
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, \
    BadSignature, SignatureExpired
from app import db, login_manager
from helper.CONSTANTS import EMAIL_REGEX, USERNAME_REGEX
from helper.helper_functions import isEmail


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
    postal_code = db.StringField(max_length=20)
    state = db.StringField(max_length=50)
    country = db.StringField(max_length=20)

    def to_json(self):
        """
        Converts and returns address object as a JSON string.
        :return address object: json string
        """
        try:
            return jsonify({
                "street": self.street,
                "city": self.city,
                "postal_code": self.postalcode,
                "state": self.state,
                "country": self.country,
            })
        except Exception as el1:
            logging.error('Unable to convert address object to json. Error={'
                          '0}'.format(el1))
            return None

    @staticmethod
    def from_json(data):
        """
        Extracts and returns address object from JSON data.
        :param data: Address object in JSON format.
        :return address: object or None
        """
        try:
            return Address(
                street=data.get('street') or '',
                city=data.get('city') or '',
                postalcode=data.get('postal_code') or '',
                state=data.get('state') or '',
                country=data.get('country') or '',
            )
        except Exception as el1:
            logging.error('Unable to extract address object from json '
                          'data provided. Error={0}'.format(el1))
            return None

    def __repr__(self):
        return '<Address: %s>' % self.street+', '+self.postalcode+', ' + \
               self.city+', '+self.country


class Tag(db.Document):
    """
    This blueprint is for Tag document. Tags can be associated to wallposts,
    comments, activities etc.
    """
    __collectionname__ = "Tag"
    id = db.SequenceField(primary_key=True)
    text = db.StringField(unique=True)

    def to_json(self):
        """
        Returns a JSON representation of Tag object.
        :return TAG: JSON object
        """
        try:
            return jsonify({
                "id": self.id,
                "text": self.text
            })
        except Exception as el1:
            logging.error('Unable to convert tag object to json. Error={'
                          '0}'.format(el1))
            return None

    @staticmethod
    def from_json(data):
        """
        Extract a tag text from json object<.
        :param data: json data containing tag object
        :return Tag: object or None
        """
        try:
            if data.get('text'):
                tag = Tag()
                tag.text = data.get('text')
                logging.info('Tag={0} successfully extracted from json '
                             'data.'.format(tag.text))
                return tag
            else:
                logging.warning('No text provided for the tag.')
                return None
        except Exception as el1:
            logging.error('Unable to store requested tag in the database. '
                          'Error={0}'.format(el1))
            return None

    @staticmethod
    def generate_fake(count=10):
        """
        This function generates dummy tags and stores them in the database.
        :param count: number of fake tags to be created
        :return:
        """
        random.seed()
        c = 0
        while c < count:
            try:
                Tag(text=forgery_py.lorem_ipsum.word()).save()
                c += 1
            except (ValidationError, NotUniqueError):
                pass
            except Exception:
                pass


class Post(db.Document):
    """
    This blueprint represents a post object. Posts are written by
    users and other users can comment on these Posts.
    """
    __collectionname__ = "Post"
    id = db.SequenceField(primary_key=True)
    body = db.StringField()
    body_html = db.StringField()
    timestamp = db.DateTimeField(default=datetime.utcnow())
    author_id = db.IntField(min_value=0)
    comments = db.ListField(db.IntField(), default=[])
    tags = db.ListField(db.IntField())

    def to_json(self):
        """
        Convert post object to JSON formatted string.
        :return post: JSON object.
        """
        try:
            return jsonify({
                "id": self.id,
                "body": self.body,
                "body_html": self.body_html,
                "timestamp": self.timestamp,
                "author": User.objects(id=self.author_id).username or '',
                "author_id": self.author_id,
                "comments": [Comment.objects(id=i).first().body for i in
                             self.comments] or [],
                "tags": [Tag.objects(id=i) for i in self.tags] or []
            })
        except Exception as el1:
            logging.error('Unable to convert post object to json. '
                          'Error={0}'.format(el1))
            return None

    @staticmethod
    def from_json(data):
        """
        Extract and returns a post object from json data provided by user.
        :param data: json data for the wall post.
        :return post: object
        """
        try:
            wp = Post()
            wp.body = data.get('body') or None
            wp.body = data.get('body_html') or None
            if wp.body is None and wp.body_html is None:
                logging.error('No data in body/body_html provided for '
                              'creating post object')
                return None
            if data.get('author_id') is None:
                logging.error('No author provided with post.')
                wp.author_id = 0
            else:
                wp.author_id = data.get('author_id')
            if data.get('tags') is not None and type(data.get('tags') is list):
                [wp.tags.append(tag) for tag in data.get('tags')]
            else:
                logging.warning('No tags loaded from the json data for '
                                'post.')
            return wp
        except Exception as el1:
            logging.error('Unable to get post object from json data. '
                          'Error={}'.format(el1))
            return None

    @staticmethod
    def generate_fake(count=10):
        """
        Generates fake post and store them in the database.
        :param count: Number of fakes wall posts to be generated.
        """
        random.seed()
        c = 0

        if User.objects.count() == 0:
            logging.error('Please generate some fake users before generating '
                          'fake posts.')
            return
        while c < count:
            try:
                tag_list = Tag.objects.values_list('id')
                wp_comment_list = Comment.objects.values_list('id')
                Post(
                    body=forgery_py.lorem_ipsum.sentences(quantity=3),
                    body_html=forgery_py.lorem_ipsum.paragraphs(
                        quantity=1, html=True, sentences_quantity=3),
                    author_id=random.choice(User.objects.values_list('id')),
                    comments=[random.choice(wp_comment_list)
                              for _ in range(0, random.randint(1, 10))],
                    tags=[random.choice(tag_list)
                          for _ in range(0, random.randint(1, 5))]
                ).save()
                c += 1
            except (ValidationError, NotUniqueError):
                pass
            except Exception:
                pass


class Comment(db.Document):
    """
    This document is the blue print for a comment. A comment may be
    associated to wallpost, activity, or any other kind of post.
    """
    __collectionname__ = "Comment"
    id = db.SequenceField(primary_key=True)
    body = db.StringField()
    body_html = db.StringField()
    timestamp = db.DateTimeField(default=datetime.utcnow())
    commenter_id = db.IntField(min_value=0)

    def to_json(self):
        """
        Convert a Comment object to json.
        :return comment: str in json format.
        """
        try:
            return jsonify({
                "id": self.id,
                "body": self.body,
                "body_html": self.body_html,
                "commenter_id": self.commenter_id,
                "commenter": User.objects(id=self.commenter_id).first().username
                             or ''
            })
        except Exception as el1:
            logging.error('Unable to convert comment object to json. Error={'
                          '0}'.format(el1))
            return None

    @staticmethod
    def from_json(data):
        """
        Store a comment from json data to the database.
        :param data: json data for the comment
        :return comment: comment object
        """
        try:
            c = Comment()
            c.body = data.get('body') or None
            c.body_html = data.get('body_html') or None
            if c.body is None and c.body_html is None:
                logging.error('No data in body/body_html provided for '
                              'creating wallpost comments object')
                return
            if data.get('commenter_id') is None:
                logging.error('No commenter specified with wallpost '
                              'comments.')
                c.commenter_id = 0
            else:
                c.commenter_id = data.get('commenter_id')
            return c
        except Exception as el1:
            logging.error('Unable to get comments object from json '
                          'data. Error={}'.format(el1))
            return

    @staticmethod
    def generate_fake(count=10):
        """
        Generates specific number of fake comments and store them in the
        database.
        :param count: Number of fakes comments to be generated.
        """
        random.seed()
        c = 0

        if User.objects.count() == 0:
            logging.error('Please generate some fake users before generating '
                          'fake wallpost comments.')
            return
        while c < count:
            try:
                Comment(
                    body=forgery_py.lorem_ipsum.sentences(quantity=1),
                    body_html=forgery_py.lorem_ipsum.paragraphs(
                        quantity=1, html=True, sentences_quantity=1),
                    commenter_id=random.choice(User.objects.values_list('id')),
                ).save()
                c += 1
            except (ValidationError, NotUniqueError):
                pass
            except Exception:
                pass


class Diary(db.Document):
    """
    This document implements model for interactive diary sessions which users
    can keep as a journal and later use for reflection purposes.
    """
    __collectionname__ = 'diary'
    id = db.SequenceField(primary_key=True)
    title = db.StringField()
    description = db.StringField()
    description_html = db.StringField()
    timestamp = db.DateTimeField(default=datetime.utcnow())
    author_id = db.IntField(min_value=0)
    tags = db.ListField(db.StringField())
    s_activity = db.ListField(db.StringField())
    s_time = db.IntField(default=0)
    o_activity = db.ListField(db.StringField())
    o_time = db.IntField(default=0)
    # No comments for personal diary

    def to_json(self):
        """
        This function converts diary document to json object.
        :return activity object: in JSON format
        """
        try:
            return jsonify({
                "id": self.id,
                "title": self.title,
                "description": self.description,
                "description_html": self.description_html,
                "timestamp": self.timestamp,
                "author_id": User.objects(id=self.author_id).first().username,
                "tags": [Tag.objects(id=i).first().text for i in self.tags],
                "study_activity": self.s_activity,
                "study_time": self.s_time,
                "other_activity": self.o_activity,
                "other_time": self.o_time
            })
        except Exception as el1:
            logging.error('Unable to convert diary object={0} to JSON format. '
                          'Error={1}'.format(self.id, el1))
            return None

    @staticmethod
    def from_json(data):
        """
        This function extracts diary object using data provided in JSON
        format and returns it to the user.
        :return activity object:
        """
        try:
            diary = Diary()
            diary.title = data.get('title') or ''
            diary.description = data.get('description') or ''
            diary.description_html = data.get('description_html') or ''
            diary.author_id = data.get('author_id') or 0
            # FIXME: All tags will be saved even if the post is not saved in db.
            if data.get('tags') and len(data.get('tags')) > 0:
                for tag in data.get('tags'):
                    if Tag.objects(text=tag).count() != 0:
                        diary.tags.append(Tag.objects(text=tag).first().id)
                    else:
                        t = Tag.from_json({'text': tag})
                        if t is not None:
                            t.save()
                            diary.tags.append(t.id)
            if data.get('s_activity') and len(data.get('s_activity')) > 0:
                diary.s_activities = data.get('s_activity')
            diary.s_time = data.get('s_time') or 0
            if data.get('o_activity') and len(data.get('o_activity')) > 0:
                diary.s_activities = data.get('o_activity')
            diary.o_time = data.get('o_time') or 0
            return diary
        except Exception as el1:
            logging.error('Unable to extract diary object from JSON. '
                          'Error={0}'.format(el1))
            return None

    @staticmethod
    def generate_fake(count=10):
        """
        This function creates and stores some fake entries in diary database
        for testing purposes
        :param count: Number of dummy diaries to be created.
        """
        random.seed()
        c = 0
        users = User.objects.values_list('id')
        tags = Tag.objects.values_list('id')
        while c < count:
            try:
                Activity(
                    title=forgery_py.lorem_ipsum.word(),
                    description=forgery_py.lorem_ipsum.sentences(quantity=2),
                    description_html=forgery_py.lorem_ipsum.paragraphs(
                        quantity=1, sentences_quantity=2, html=False),
                    tags=[random.choice(tags)
                          for _ in range(1, random.randint(1, 5))],
                    author_id=random.choice(users),
                    s_activity=[forgery_py.lorem_ipsum.word()
                                for _ in range(1, 5)],
                    s_time=random.randint(1, 5),
                    o_activity=[forgery_py.lorem_ipsum.word()
                                for _ in range(1, 5)],
                    o_time=random.randint(1, 5),
                ).save()
            except (ValidationError, NotUniqueError):
                pass
            except Exception:
                pass


class Activity(db.Document):
    """
    This document implements the model for Activities. Any user can post the
    activities. and other people can comment on them as well as decide to
    join to show their interest in the activities.
    """
    __collectionname__ = 'activity'
    id = db.SequenceField(primary_key=True)
    title = db.StringField()
    description = db.StringField()
    description_html = db.StringField()
    timestamp = db.DateTimeField(default=datetime.utcnow())
    activity_time = db.DateTimeField()
    tags = db.ListField(db.StringField())
    interested = db.ListField(db.IntField(min_value=1))
    going = db.ListField(db.IntField(min_value=1))
    comments = db.ListField(db.StringField())     # string must be Comment:json

    def to_json(self):
        """
        This function returns the json representation of activity object.
        :return:
        """
        try:
            return jsonify({
                "id": self.id,
                "title": self.title,
                "description": self.description,
                "description_html": self.description_html,
                "timestamp": self.timestamp,
                "activity_time": self.activity_time,
                "tags": [Tag.objects(id=i).first().text for i in self.tags],
                "interested": [User.objects(id=i).first().username
                               for i in self.interested],
                "going": [User.objects(id=i).first().username
                          for i in self.going],
                "comments": [Comment.objects(id=i).first().body
                             for i in self.comments]
            })
        except Exception as el1:
            logging.error('Unable to convert activity object={0} to JSON. '
                          'Error{1}'.format(self.id, el1))
            return None

    @staticmethod
    def from_json(data):
        """
        This function creates and returns activity object from json data.
        :param data: json formatted string containing activity data.
        :return activity: object
        """
        try:
            activity = Activity()
            activity.title = data.get('title') or ''
            activity.description = data.get('description') or ''
            activity.description_html = data.get('description_html') or ''
            activity.activity_time = data.get('activity_time') or ''
            # FIXME: All tags will be saved even if the post is not saved in db.
            if data.get('tags') and len(data.get('tags')) > 0:
                for tag in data.get('tags'):
                    if Tag.objects(text=tag).count() != 0:
                        activity.tags.append(Tag.objects(text=tag).first().id)
                    else:
                        t = Tag.from_json({'text': tag})
                        t.save()
                        activity.tags.append(t.id)
            if data.get('interested') and len(data.get('interested')) > 0:
                activity.interested = data.get('interested')
            if data.get('going') and len(data.get('going')) > 0:
                activity.going = data.get('going')
            # FIXME: All comments will be saved even if the post is not saved.
            if data.get('comments') and len(data.get('comments')) > 0:
                for comment in data.get('comments'):
                    try:
                        c = Comment.from_json(comment)
                        c.save()
                        activity.comments.append(c.id)
                    except Exception:
                        pass
            return activity
        except Exception as el1:
            logging.error('Unable to extract activity object from JSON data. '
                          'Error={0}'.format(el1))
            return None

    @staticmethod
    def generate_fake(count=10):
        """
        This function generates and stores fake enteries for Activity
        documents for
        testing purposes.
        :param count: number of fake activity entries to be generated.
        """

        random.seed()
        c = 0
        tags = Tag.objects.values_list('id')
        comments = Comment.objects.values_list('id')
        users = User.objects.values_list('id')
        while c < count:
            try:
                Activity(
                    title=forgery_py.lorem_ipsum.sentence(),
                    description=forgery_py.lorem_ipsum.sentences(quantity=2),
                    description_html=forgery_py.lorem_ipsum.paragraph(
                        sentences_quantity=2, html=True),
                    activity_time=datetime.utcnow()+timedelta(
                        days=random.randint(1, 7)),
                    tags=[random.choice(tags)
                          for _ in range(1, random.randint(1, 5))],
                    comments=[random.choice(comments)
                              for _ in range(1, random.randint(1, 5))],
                    interested=[random.choice(users)
                                for _ in range(1, random.randint(1, 7))],
                    going=[random.choice(users)
                           for _ in range(1, random.randint(1, 5))],
                ).save()
            except (ValidationError, NotUniqueError):
                pass
            except Exception:
                pass


class Suggestion(db.Document):
    """
    This document represents database model for suggestions data. Each
    suggestion item is a query with a set of associated replies displayed to
    user depending on the matched query.
    """
    __collectionname__ = 'suggestion'
    id = db.SequenceField(primary_key=True)
    query = db.StringField()
    responses = db.ListField(db.StringField())

    def to_json(self):
        """
        This function converts suggestions item to JSON representation to
        return it to the user.
        :return suggestions object: JSON representation.
        """
        try:
            return {
                "id": self.id,
                "query": self.query,
                "responses": self.responses
            }
        except Exception as el1:
            logging.error('Unable to convert suggestion document to json '
                          'format. Error{0}'.format(el1))
            return None

    @staticmethod
    def from_json(data):
        """
        This function converts suggestions object's JSON representation to
        database object and return it.
        :param data: json representation of suggestion object.
        :return suggestion: object.
        """
        try:
            s = Suggestion()
            s.query = data.get('query')
            s.responses = data.get('responses')
            return s
        except Exception as e:
            logging.error('Unable to load suggestion from json data. '
                          'Error={0}'.format(e))
            return None

    @staticmethod
    def generate_fake(count=10):
        """
        This function generates a set of fake suggestion queries and their
        responses for testing purposes.
        :param count: Number of fake suggestion queries and reponses to develop.
        :return:
        """

        random.seed()
        c = 0
        while c < count:
            try:
                Suggestion(query=forgery_py.lorem_ipsum.sentence(),
                           responses=[forgery_py.lorem_ipsum.sentence() for _
                                      in range(0, random.randint(1, 5))]).save()
                c += 1
            except (ValidationError, NotUniqueError):
                pass
            except Exception:
                pass

    @staticmethod
    def load_data_from_csv(filepath):
        """
        This function reads a .csv file containing possible queries and their
         possible answers.
        :param filepath: path to csv file for lading
        :return:
        """
        count = 0
        try:
            with open(filepath, 'r') as f:
                next(f)
                for line in f:
                    data = line.split(',')
                    try:
                        Suggestion(query=data[0], responses=data[1:]).save()
                        count += 1
                    except Exception:
                        pass
            logging.info('{0} entries read to suggestion table from csv '
                         'file.'.format(count))
            return count
        except Exception as el1:
            logging.error('Unable to load suggestion data from csv file. '
                          'Error={0}'.format(el1))


class User(UserMixin, db.Document):
    """
    User document structure.
    """
    # FIXME: Decide a schema and move to Document instead of Dynamic document.
    __collectionname__ = 'user'
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
    role = db.IntField(default=0) 	# User:0, Student=1, Parent=2, Teacher=3

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
    kids = db.ListField(db.IntField(min_value=1), default=[])

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
                self.permissions = Permission.PERM_ADMIN
            if self.permissions is None:
                self.permissions = Permission.PERM_ADMIN
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8'))\
                                      .hexdigest()

    def set_password(self, password):
        """
        Generate and store password hash for the user.
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
        Returns if a user has enough permission to perform an operation.
        :param permission: Permission name.
        :return: True if user has a permission.
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
        email address) of valid user. This token contains the changed
        username/email information of user and using this token will
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
        :return: url for user's avatar icon.
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
        Gives a json representation of the user.
        :return: json representation of user document.
        """
        json_user = {
            'url': url_for('api.get_user', sub_id=self.id,
                           _external=True),
            'username': self.username,
            'name': '%s %s' % (self.first_name, self.last_name),
            'address': self.address.to_json() if self.address else '',
            'company': self.company,
            'phone': self.phone,
            'email': self.email,
        }
        return json_user

    @staticmethod
    def from_json(data):
        """
        Register a new user document from the json data.
        :return: User object that is created from json data.
        """
        try:
            user = User(username=data.get('username'),
                        email=data.get('email'))
            if data.get('password') is None:
                return None
            user.set_password(data.get('password'))
            if data.get('name') is not None:
                user.first_name = data.get('name')['first'] or ''
                user.last_name = data.get('name')['last'] or ''
            user.company = data.get('company') or ''
            user.phone = data.get('phone') or ''
            user.address = Address.from_json(data.get('address')) \
                if data.get('address') else None
            return user
        except Exception as el1:
            logging.error('Unable to load user object from json data. Error={'
                          '0}'.format(el1))
            return None

    def update_from_json(self, data):
        """
        Update the user document from json data.
        Note: username, email and password must be changed using tokens only.
        """
        if data.get('name') is not None:
            self.first_name = data.get('name')['first'] or self.first_name
            self.last_name = data.get('name')['last'] or self.last_name
        self.company = data.get('company') or self.company
        self.phone = data.get('phone') or self.phone
        if data.get('address') is not None:
            self.address = Address.from_json(data.get('address'))
        self.save()

    def is_teacher(self):
        """
        Checks whether given user is a teacher
        """
        return True if self.role == 3 else False

    def is_parent(self):
        """
        Checks whether given user is a parent
        """
        return True if self.role == 2 else False

    def is_student(self):
        """
        Checks whether given user is a student
        """
        return True if self.role == 1 else False

    def is_student_of(self, user):
        """
        Checks whether given user is a student of another user
        """
        return True if user.id in self.teaching else False

    def is_child_of(self, user):
        """
        Checks whether given user is a child of another user
        """
        return True if user.id in self.parents else False

    def is_friend_of(self, user):
        """
        Checks whether given user is a friend of another user
        """
        return True if user.id in self.friends else False

    def __repr__(self):
        return '<User %r>' % self.username

    @staticmethod
    def generate_fake(count=10):
        """
        Generates fake users and store them in the database.
        :param count: Number of fakes users to be generated.
        """
        random.seed()
        c = 0
        while c < count:
            try:
                user = User(
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
                user.address = address
                user.confirmed = True
                user.set_password('password')
                user.save()
                c += 1
            except (ValidationError, NotUniqueError):
                pass
            except Exception:
                pass


@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=int(user_id)).first()
