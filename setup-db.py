from server import db, app
import os

user_type_data = [
	{ 'id': 1, 'description': 'Super User' },
	{ 'id': 2, 'description': 'Customer' },
]

user_data = [
	{ 'username': 'user1', 'password': 'pass', 'user_type_id': 2, 'organization_id': None },
	{ 'username': 'user2', 'password': 'pass', 'user_type_id': 2, 'organization_id': 2 },
	{ 'username': 'user3', 'password': 'pass', 'user_type_id': 2, 'organization_id': 2 },
	{ 'username': 'user4', 'password': 'pass', 'user_type_id': 2, 'organization_id': 3 },
	{ 'username': 'user5', 'password': 'pass', 'user_type_id': 2, 'organization_id': 1 },
	{ 'username': 'user6', 'password': 'pass', 'user_type_id': 2, 'organization_id': 4 },
	{ 'username': 'user7', 'password': 'pass', 'user_type_id': 2, 'organization_id': 2 },
]

organization_data = [
	{ 'id': 1, 'name': 'Test Inc' },
	{ 'id': 2, 'name': 'Sample Co' },
	{ 'id': 3, 'name': 'Spelunker\' Union' },
	{ 'id': 4, 'name': 'Data Denizens' },
]

permission_data = [
	{ 'id': 1, 'description': 'Permission 1' },
	{ 'id': 2, 'description': 'Permission 2' },
	{ 'id': 3, 'description': 'Permission 3' },
]

user_permission_data = [
	{ 'user_id': 1, 'permission_id': 1 },
	{ 'user_id': 1, 'permission_id': 2 },
	{ 'user_id': 1, 'permission_id': 3 },
	{ 'user_id': 2, 'permission_id': 3 },
	{ 'user_id': 3, 'permission_id': 2 },
]

category_data = [
	{ 'id': 1, 'name': 'Computers' },
	{ 'id': 2, 'name': 'Sports' },
	{ 'id': 3, 'name': 'Furniture' },
]

product_data = [
	{ 'id': 1, 'name': 'Macbook Pro',  'category_id': 1 },
	{ 'id': 2, 'name': 'Zenbook', 'category_id': 1 },
	{ 'id': 3, 'name': 'Surface Pro', 'category_id': 1 },
	{ 'id': 4, 'name': 'Lenovo W530', 'category_id': 1 },
	{ 'id': 5, 'name': 'Acer Laptop', 'category_id': 1 },
	{ 'id': 6, 'name': 'Baseball Bat', 'category_id': 2 },
	{ 'id': 7, 'name': 'Baseball Mitt', 'category_id': 2 },
	{ 'id': 8, 'name': 'Basketball', 'category_id': 2 },
	{ 'id': 9, 'name': 'Running Shoes', 'category_id': 2 },
	{ 'id': 10, 'name': 'Hockey Stick', 'category_id': 2 },
	{ 'id': 11, 'name': 'Skates', 'category_id': 2 },
	{ 'id': 12, 'name': 'Desk', 'category_id': 3 },
	{ 'id': 13, 'name': 'Chair', 'category_id': 3 },
	{ 'id': 14, 'name': 'Couch', 'category_id': 3 },
	{ 'id': 15, 'name': 'Book Case', 'category_id': 3 },
	{ 'id': 16, 'name': 'Mantle', 'category_id': 3 },
	{ 'id': 17, 'name': 'Sofa', 'category_id': 3 },
]

def add_users(db):
	for row in user_data:
		db.session.execute(
			'''
				insert into user(username, password, user_type_id, organization_id)
				values ( :username, :password, :user_type_id, :organization_id )
			''',
			row
		)

def add_permissions(db):
	for row in permission_data:
		db.session.execute(
			'insert into permission(id, description) values ( :id, :description )',
			row
		)

def add_user_permission(db):
	for row in user_permission_data:
		db.session.execute(
			'insert into user_permission(user_id, permission_id) values ( :user_id, :permission_id )',
			row
		)

def add_user_types(db):
	for row in user_type_data:
		db.session.execute(
			'insert into user_type(id, description) values( :id, :description )',
			row
		)

def add_organizations(db):
	for row in organization_data:
		db.session.execute(
			'insert into organization(id, name) values( :id, :name )',
			row
		)

def add_categories(db):
	for row in category_data:
		db.session.execute(
			'insert into category(id, name) values( :id, :name )',
			row
		)

def add_products(db):
	for row in product_data:
		db.session.execute(
			'insert into product(id, name, category_id) values( :id, :name, :category_id )',
			row
		)

def seed_database(db):
	# Tables inserts need to be ordered to avoid foreign key issues
	add_user_types(db)
	add_organizations(db)
	add_users(db)
	add_permissions(db)
	add_user_permission(db)
	add_categories(db)
	add_products(db)
	db.session.commit()

def main():
	if os.path.isfile('mydb.sqlite'):
		os.remove('mydb.sqlite')

	with app.test_request_context():
		db.init_app(app)
		# Import all models after connecting db to app instance
		import server.models
		db.create_all()
		seed_database(db)

if __name__ == '__main__':
	main()