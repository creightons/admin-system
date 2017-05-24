from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired

class NewOrganizationForm(Form):
	name = StringField('Name', validators = [InputRequired()])

class EditUserForm(Form):
	username = StringField('Username', validators = [InputRequired()])
	password = PasswordField('New Password')
	first_name = StringField('First Name')
	last_name = StringField('Last Name')

class AddUserForm(Form):
	username = StringField('Username', validators = [InputRequired()])
	password = PasswordField('Password', validators = [InputRequired()])
	first_name = StringField('First Name', validators = [InputRequired()])
	last_name = StringField('Last Name', validators = [InputRequired()])