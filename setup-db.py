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

def add_users(db, users):
	for row in users:
		db.session.execute(
			'''
				insert into user(username, password, user_type_id, organization_id)
				values ( :username, :password, :user_type_id, :organization_id )
			''',
			row
		)
		#user = server.models.User(row['username'], row['password'], row['user_type'])
		#db.session.add(user)

def add_user_types(db, types):
	for row in types:
		#user_type = server.models.UserType(row['id'], row['description'])
		#db.session.add(user_type)
		db.session.execute(
			'insert into user_type(id, description) values( :id, :description )',
			row
		)

def add_organizations(db, organizations):
	for row in organizations:
		#organization = server.models.Organization(row['description'])
		#db.session.add(organization)
		db.session.execute(
			'insert into organization(id, name) values( :id, :name )',
			row
		)

def seed_database(db):
	add_users(db, user_data)
	add_user_types(db, user_type_data)
	add_organizations(db, organization_data)
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