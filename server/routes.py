from __future__ import print_function
import sys
from flask import render_template, request, session, redirect
from database import db
from models import User, Organization, Category, Product
from main import app
from middleware import is_authorized
from forms import NewOrganizationForm, AddUserForm, EditUserForm, \
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
		form = NewOrganizationForm()
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
		form = NewOrganizationForm()
		fields = [ form.name, form.csrf_token ]

		if form.validate_on_submit():
			new_organization = Organization(request.form['name'])
			db.session.add(new_organization)
			db.session.commit()
			return redirect('/organizations')

		return render_template(
			'add_organization.html',
			fields = fields
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

		if organization == None:
			return render_template('404.html')

		form = NewOrganizationForm()
		fields = [ form.name, form.csrf_token ]

		if form.validate_on_submit():
			updated_organization = Organization.query.filter_by(id = organization_id).update({
				'name': form.name.data
			})

			db.session.commit()

			return redirect('/organizations')

		form.name.data = organization.name
		fields = [ form.name, form.csrf_token ]

		postback_url = '/edit-organization/' + str(organization_id)

		return render_template(
			'edit_organization.html',
			fields = fields,
			postback_url = postback_url
		)


	@app.route('/users', methods = ['GET'])
	def show_users():
		users = User.query.all()
		user_list = [ { 'name': u.username , 'link': '/edit-user/' + str(u.id) }
			for u in users ]
		return render_template('users.html', users = user_list)

	@app.route('/add-user', methods = ['GET', 'POST'])
	def add_user():
		form = AddUserForm()
		form.organization.choices = BLANK_CHOICE + [ (o.id, o.name) for o in Organization.query.all() ]
		fields = [
			form.username,
			form.password,
			form.first_name,
			form.last_name,
			form.csrf_token,
		]

		if form.validate_on_submit():
			new_user = User(request.form['username'], request.form['password'])
			new_user.first_name = request.form['first_name']
			new_user.last_name = request.form['last_name']
			if form.organization.data is not None:
				new_user.organization_id = form.organization.data
			else:
				new_user.organization_id = None

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
		form = EditUserForm()

		user = User.query.filter_by(id = user_id).first()
		postback_url = '/edit-user/' + str(user_id)

		form.organization.choices = BLANK_CHOICE + [ (o.id, o.name) for o in Organization.query.all() ]

		if form.validate_on_submit():
			updates = {}
			updates['username'] = form.username.data
			updates['first_name'] = form.first_name.data
			updates['last_name'] = form.last_name.data
			updates['organization_id'] = form.organization.data

			if form.password.data != '':
				updates['password'] = form.password.data

			User.query.filter_by(id = user_id).update(updates)

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
		categories = [
			{
				'name': c.name,
				'link': '/edit-category/' + str(c.id),
			} for c in Category.query.all()
		]

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
		products = [
			{
				'name': p.name,
				'link': '/edit-product/' + str(p.id),
			} for p in Product.query.all()
		]

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