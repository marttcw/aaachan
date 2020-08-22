import re
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileRequired
from wtforms import Form, BooleanField, StringField, PasswordField, TextAreaField, SelectField, MultipleFileField
from wtforms.validators import Length, DataRequired, EqualTo, NumberRange
from wtforms.fields.html5 import IntegerField

class SetupForm(FlaskForm):
    site_name = StringField('Site Name', [Length(min=1, max=64)])
    admin_username = StringField('Admin Username', [Length(min=1, max=64)])
    password = PasswordField('New Password', [
        DataRequired(),
        EqualTo('confirm', message='Passwords must match'),
        Length(min=8, max=256)
    ])
    confirm = PasswordField('Repeat Password')

class NewModForm(FlaskForm):
    username = StringField('Username', [Length(min=1, max=64)])
    password = PasswordField('New Password', [
        DataRequired(),
        EqualTo('confirm', message='Passwords must match'),
        Length(min=8, max=256)
    ])
    confirm = PasswordField('Repeat Password')

class NewBoardForm(FlaskForm):
    directory = StringField('Directory', [
        DataRequired(),
        Length(min=1, max=256)
    ])
    name = StringField('Name', [
        DataRequired(),
        Length(min=1, max=256)
    ])
    description = TextAreaField('Description')

    btype = SelectField('Type', [
            DataRequired()
        ], choices=[
            ('i', 'Imageboard'),
            ('t', 'Textboard'),
            ('b', 'Booru')
        ])

    category = SelectField('Category', [
            DataRequired()
        ], coerce=int)

    new_category = StringField('New Category (Created if selected)', [
    ])

    nsfw = BooleanField('NSFW')

    files_types = StringField('Files Types (seperate by space)', [])
    files_limit = IntegerField('Files Amount Limit', [
            NumberRange(min=0, max=10)
        ])

class LoginForm(FlaskForm):
    username = StringField('Username', [
        DataRequired()
    ])
    password = PasswordField('Password', [
        DataRequired()
    ])

class NewThreadForm(FlaskForm):
    title = StringField('Title', [
        DataRequired(),
        Length(min=1, max=256)
    ])
    options = StringField('Options')
    content = TextAreaField('Content', [
        DataRequired()
    ])
    files = MultipleFileField('Files')

    # Honeypots
    name = StringField('Name')
    message = TextAreaField('Message')

class NewPostForm(FlaskForm):
    title = StringField('Title')
    options = StringField('Options')
    content = TextAreaField('Content', [
        DataRequired()
    ])
    files = MultipleFileField('Files')

    # Honeypots
    name = StringField('Name')
    message = TextAreaField('Message')

class EditBoardForm(FlaskForm):
    name = StringField('Name', [
        DataRequired(),
        Length(min=1, max=256)
    ])
    description = TextAreaField('Description')

    btype = SelectField('Type', [
            DataRequired()
        ], choices=[
            ('i', 'Imageboard'),
            ('t', 'Textboard'),
            ('b', 'Booru')
        ])

    category = SelectField('Category', [
            DataRequired()
        ], coerce=int)

    new_category = StringField('New Category (Created if selected)', [
    ])

    nsfw = BooleanField('NSFW')

    files_types = StringField('Files Types (seperate by space)', [])
    files_limit = IntegerField('Files Amount Limit', [
            NumberRange(min=0, max=10)
        ])

class ReportForm(FlaskForm):
    reason = StringField('Reason', [
        DataRequired(),
        Length(min=1, max=256)
    ])

