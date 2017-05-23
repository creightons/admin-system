from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import InputRequired

class NewOrganizationForm(Form):
	name = StringField('Name', validators = [InputRequired()])


class UserForm(Form):
	username = StringField('Username', validators = [InputRequired()])