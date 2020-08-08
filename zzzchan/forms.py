from wtforms import Form, BooleanField, StringField, PasswordField, validators, TextAreaField

class SetupForm(Form):
    site_name = StringField('Site Name', [validators.Length(min=1, max=64)])
    admin_username = StringField('Admin Username', [validators.Length(min=1, max=64)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match'),
        validators.Length(min=8, max=256)
    ])
    confirm = PasswordField('Repeat Password')

class NewBoardForm(Form):
    directory = StringField('Directory', [
        validators.DataRequired(),
        validators.Length(min=1, max=256)
    ])
    name = StringField('Name', [
        validators.DataRequired(),
        validators.Length(min=1, max=256)
    ])
    description = TextAreaField('Description')

class LoginForm(Form):
    username = StringField('Username', [
        validators.DataRequired()
    ])
    password = PasswordField('Password', [
        validators.DataRequired()
    ])

