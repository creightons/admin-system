from database import db

# UserType Constants (Type => ID)
SUPERUSER = 1

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True, nullable = False)
	username = db.Column(db.String(20), unique = True, nullable = False)
	password = db.Column(db.String(20), nullable = False)
	first_name = db.Column(db.String(20))
	last_name = db.Column(db.String(20))
	user_type_id = db.Column(
		db.Integer,
		db.ForeignKey('user_type.id'),
		nullable = False,
		default = SUPERUSER
	)
	organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))

	def __init__(self, username, password):
		self.username = username
		self.password = password

class UserType(db.Model):
	__tablename__ = 'user_type'
	id = db.Column(db.Integer, primary_key = True, nullable = False)
	description = db.Column(db.String(20), nullable = False)
	users = db.relationship('User',	backref = 'user_type', lazy = 'dynamic')

	def __init__(self, description):
		self.description = description

class Organization(db.Model):
	id = db.Column(db.Integer, primary_key = True, nullable = False)
	name = db.Column(db.String(20), nullable = False)

	def __init__(self, name):
		self.name = name

class Product(db.Model):
	id = db.Column(db.Integer, primary_key = True, nullable = False)
	name = db.Column(db.String(40), nullable = False)
	category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

	def __init__(self, name, category_id):
		self.name = name
		self.category_id = category_id

class Category(db.Model):
	id = db.Column(db.Integer, primary_key = True, nullable = False)
	name = db.Column(db.String(40), nullable = False)
	products = db.relationship('Product', backref = 'category', lazy = 'dynamic')

	def __init__(self, name):
		self.name = name