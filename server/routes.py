from __future__ import print_function
import sys
from flask import render_template, request, session, redirect
from database import db
from models import User, Organization, Category, Product, Permission
from main import app
from middleware import is_authorized
from forms import OrganizationForm, AddUserForm, EditUserForm, \
	CategoryForm, ProductForm


###################################
# Constants
###################################
# If a user does not select to be part of an organization, they
# will choose this option which means they are not in an organization
NO_ORGANIZATION_ID = 0
BLANK_CHOICE = [ (NO_ORGANIZATION_ID, '(None)') ]


def apply_routes(app):

	@app.route('/', methods = ['GET'])
	def index():
		return render_template('index.html')

	@app.route('/login', methods = ['POST'])
	def login():
		user = User.query.filter_by(
			username = request.form['username'],
			password = request.form['password']
		).first()

		if user == None:
			return redirect('/')
		else:
			session['username'] = request.form['username']
			return redirect('/dashboard')

	@app.route('/logout', methods = ['GET'])
	def logout():
		session.pop('username', None)
		return redirect('/')

	@app.route('/dashboard', methods = ['GET'])
	@is_authorized
	def dashboard():
		users = User.query.all()
		organizations = Organization.query.all()

		user_list = [ user.username for user in users ]
		organization_list = [ organization.name for organization in organizations ]
		return render_template(
			'dashboard.html',
			user_list = user_list,
			organization_list = organization_list
		)

	@app.route('/organizations', methods = ['GET', 'POST'])
	def organizations_page():
		form = OrganizationForm()
		fields = [ form.name, form.csrf_token ]

		if form.validate_on_submit():
			new_organization = Organization(request.form['name'])
			db.session.add(new_organization)
			db.session.commit()
			return redirect('/dashboard')

		organizations = Organization.query.all()
		organization_list = [
			{
				'name': org.name,
				'link': '/edit-organization/' + str(org.id),
				'delete_link': '/delete-organization/' + str(org.id),
			} for org in organizations
		]

		return render_template(
			'organizations.html',
			organizations = organization_list,
			fields = fields,
			form = form
		)

	@app.route('/add-organization', methods = ['GET', 'POST'])
	def add_organization():
		categories = Category.query.all()
		category_options = [{
			'description': c.name,
			'field_id': c.id,
			'checkbox': False,
		} for c in categories]

		form = OrganizationForm(formdata = request.form, categories = category_options)

		if form.validate_on_submit():
			new_organization = Organization(request.form['name'])
			selected_category_map = { int(category_data['field_id']) : True
				for category_data in form.categories.data if category_data['checkbox'] == True }
			new_organization.categories = [ c for c in categories if c.id in selected_category_map ]
			db.session.add(new_organization)
			db.session.commit()
			return redirect('/organizations')

		return render_template(
			'organization_form.html',
			postback_url = '/add-organization',
			form = form,
			title = 'Add Organization'
		)

	
	@app.route('/delete-organization/<int:organization_id>', methods = ['POST'])
	def delete_organization(organization_id):
		organization = Organization.query.filter_by(id = organization_id).first()
		db.session.delete(organization)
		db.session.commit()
		return redirect('/organizations')

	@app.route('/edit-organization/<int:organization_id>', methods = ['GET', 'POST'])
	def edit_organization(organization_id):
		organization = Organization.query.filter_by(id = organization_id).first()
		postback_url = '/edit-organization/' + str(organization_id)

		if organization == None:
			return render_template('404.html')

		categories = Category.query.all()
		category_options = [{
			'description': c.name,
			'field_id': c.id,
			'checkbox': False,
		} for c in categories]

		form = OrganizationForm(formdata = request.form, categories = category_options)

		if form.validate_on_submit():
			organization.name = form.name.data

			selected_category_map = { int(category_data['field_id']) : True
				for category_data in form.categories.data if category_data['checkbox'] == True }
			organization.categories = [ c for c in categories if c.id in selected_category_map ]

			db.session.commit()

			return redirect(postback_url)

		form.name.data = organization.name


		return render_template(
			'organization_form.html',
			form = form,
			postback_url = postback_url,
			title = 'Edit Organization'
		)


	@app.route('/users', methods = ['GET'])
	def show_users():
		users = User.query.all()
		user_list = [ { 'name': u.username , 'link': '/edit-user/' + str(u.id) }
			for u in users ]
		return render_template('users.html', users = user_list)

	@app.route('/add-user', methods = ['GET', 'POST'])
	def add_user():
		permissions = Permission.query.all()

		permissions_options = [{
			'description': p.description,
			'field_id': p.id,
			'checkbox': False,
		} for p in  permissions]

		form = AddUserForm(formdata = request.form, permissions = permissions_options)
		form.organization.choices = BLANK_CHOICE + [ (o.id, o.name) for o in Organization.query.all() ]

		if form.validate_on_submit():
			new_user = User(request.form['username'], request.form['password'])
			new_user.first_name = request.form['first_name']
			new_user.last_name = request.form['last_name']
			if form.organization.data == 0:
				new_user.organization_id = None
			else:
				new_user.organization_id = form.organization.data

			# Make a map of the ids the user selected
			user_perm_id_map = { int(permission_data['field_id']) : True
				for permission_data in form.permissions.data if permission_data['checkbox'] == True }
			# Grab the permissions that match the ones the user selected and asign them to the family
			new_user.permissions =  [ p for p in permissions if p.id in user_perm_id_map ]

			db.session.add(new_user)
			db.session.commit()
			return redirect('/users')

		return render_template(
			'user_form.html',
			title = 'Add User',
			form = form,
			postback_url = '/add-user'
		)


	@app.route('/edit-user/<int:user_id>', methods = ['GET', 'POST'])
	def edit_user(user_id):
		user = User.query.filter_by(id = user_id).first()
		user_permissions = { p.id : True for p in user.permissions }

		permissions = Permission.query.all()
		permissions_options = [{
			'description': p.description,
			'field_id': p.id,
			'checkbox': True if p.id in user_permissions else False,
		} for p in  permissions]

		form = EditUserForm(formdata = request.form, permissions = permissions_options)
		postback_url = '/edit-user/' + str(user_id)

		form.organization.choices = BLANK_CHOICE + [ (o.id, o.name) for o in Organization.query.all() ]

		if form.validate_on_submit():
			user.username = form.username.data
			user.first_name = form.first_name.data
			user.last_name = form.last_name.data
			user.organization_id = form.organization.data

			# Make a map of the ids the user selected
			user_perm_id_map = { int(permission_data['field_id']) : True
				for permission_data in form.permissions.data if permission_data['checkbox'] == True }
			# Grab the permissions that match the ones the user selected and asign them to the family
			user.permissions =  [ p for p in permissions if p.id in user_perm_id_map ]

			if form.password.data != '':
				user.password = form.password.data

			db.session.commit()
			return redirect(postback_url)

		form.username.data = user.username
		form.password.data = user.password
		form.first_name.data = user.first_name
		form.last_name.data = user.last_name
		form.organization.data = user.organization_id or NO_ORGANIZATION_ID

		return render_template(
			'user_form.html',
			title = 'Edit User',
			form = form,
			postback_url = postback_url
		)


	@app.route('/categories')
	def show_categories():
		categories = [{
			'name': c.name,
			'link': '/edit-category/' + str(c.id),
		} for c in Category.query.all()]

		return render_template('categories.html', categories = categories)


	@app.route('/add-category', methods = ['GET', 'POST'])
	def add_category():
		form = CategoryForm()

		if form.validate_on_submit():
			category = Category(form.name.data)
			db.session.add(category)
			db.session.commit()
			return redirect('/categories')

		return render_template(
			'category_form.html',
			title = 'Add Category',
			form = form,
			postback_url = '/add-category'
		)


	@app.route('/edit-category/<int:category_id>', methods = ['GET', 'POST'])
	def edit_category(category_id):
		form = CategoryForm()
		category = Category.query.filter_by(id = category_id).first()
		postback_url = '/edit-category/' + str(category_id)

		if form.validate_on_submit():
			category.name = form.name.data
			db.session.commit()
			return redirect('/categories')


		form.name.data = category.name
		return render_template(
			'category_form.html',
			title = 'Edit Category',
			form = form,
			postback_url = postback_url
		)


	@app.route('/products')
	def show_products():
		products = [ { 'name': p.name, 'link': '/edit-product/' + str(p.id) }
			for p in Product.query.all()]
		return render_template('products.html', products = products)

	@app.route('/add-product', methods = ['GET', 'POST'])
	def add_product():
		form = ProductForm()
		form.category.choices = [ (c.id, c.name) for c in Category.query.all() ]

		if form.validate_on_submit():
			product = Product(form.name.data, form.category.data)
			db.session.add(product)
			db.session.commit()
			return redirect('/products')

		return render_template(
			'product_form.html',
			title = 'Add Product',
			form = form,
			postback_url = '/add-product'
		)


	@app.route('/edit-product/<int:product_id>', methods = ['GET', 'POST'])
	def edit_product(product_id):
		form = ProductForm()
		form.category.choices = [ (c.id, c.name) for c in Category.query.all() ]
		product = Product.query.filter_by(id = product_id).first()
		postback_url = '/edit-product/' + str(product_id)

		if form.validate_on_submit():
			product.name = form.name.data
			product.category_id = form.category.data
			db.session.commit()
			return redirect('/products')

		form.name.data = product.name
		form.category.data = product.category_id

		return render_template(
			'product_form.html',
			title = 'Edit Product',
			form = form,
			postback_url = postback_url
		)

	@app.route('/permissions')
	def show_permissions():
		permissions = [	{ 'name': p.description } for p in Permission.query.all() ]
		return render_template('permissions.html', permissions = permissions)