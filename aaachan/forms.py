import re
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileRequired
from wtforms import Form, BooleanField, StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import Length, DataRequired, EqualTo

class SetupForm(FlaskForm):
    site_name = StringField('Site Name', [Length(min=1, max=64)])
    admin_username = StringField('Admin Username', [Length(min=1, max=64)])
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

    nswf = BooleanField('NSFW')

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
    image = FileField('Image file', [FileRequired()])

class NewPostForm(FlaskForm):
    title = StringField('Title')
    options = StringField('Options')
    content = TextAreaField('Content', [
        DataRequired()
    ])
    image = FileField('Image file')

