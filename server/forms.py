from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, \
	HiddenField, FieldList, FormField
from wtforms.validators import InputRequired

# Wraps the BooleanField class so that it may be used in
# a FieldList object. See last comment in:
#	 https://github.com/wtforms/wtforms/issues/308
class BooleanSubField(BooleanField):
    def process_data(self, value):
        if isinstance(value, BooleanField):
            self.data = value.data
        else:
            self.data = bool(value)

class OptionForm(FlaskForm):
	description = HiddenField('Description')
	field_id = HiddenField('Field Id')
	checkbox = BooleanSubField('Member', default = False)

class OrganizationForm(FlaskForm):
	name = StringField('Name', validators = [InputRequired()])
	categories = FieldList(FormField(OptionForm))


# To add data to "organizations" when initializing an object from this class,
# call this class as:
#	form = EditUserForm(organizations = list_of_dicts)
# where:
#	list_of_dicts = [ { 'description': <str>, 'checkbox': <bool> }, ... ]
class EditUserForm(FlaskForm):
	username = StringField('Username', validators = [InputRequired()])
	password = PasswordField('New Password')
	first_name = StringField('First Name')
	last_name = StringField('Last Name')
	# organization stores an organization_id
	organization = SelectField('Organization', coerce = int)
	permissions = FieldList(FormField(OptionForm))

class AddUserForm(FlaskForm):
	username = StringField('Username', validators = [InputRequired()])
	password = PasswordField('Password', validators = [InputRequired()])
	first_name = StringField('First Name', validators = [InputRequired()])
	last_name = StringField('Last Name', validators = [InputRequired()])
	organization = SelectField(
		'Organization',
		coerce = int,
		validators = [InputRequired()]
	)
	permissions = FieldList(FormField(OptionForm))

class CategoryForm(FlaskForm):
	name = StringField('Name', validators = [InputRequired()])

class ProductForm(FlaskForm):
	name = StringField('Name', validators = [InputRequired()])
	category = SelectField(
		'Category',
		coerce = int,
		validators = [InputRequired()]
	)