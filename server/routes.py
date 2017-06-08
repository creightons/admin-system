from __future__ import print_function
import sys
from flask import render_template, request, session, redirect, url_for
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

        @app.route('/')
        def customer_page():
            return render_template('customer_page.html')

	@app.route('/admin', methods = ['GET'])
	def index():
		return render_template('index.html')

	@app.route('/admin/login', methods = ['POST'])
	def login():
		user = User.query.filter_by(
			username = request.form['username'],
			password = request.form['password']
		).first()

		if user == None:
			return redirect(url_for('index'))
		else:
			session['username'] = request.form['username']
			return redirect(url_for('dashboard'))

	@app.route('/admin/logout', methods = ['GET'])
	def logout():
		session.pop('username', None)
		return redirect(url_for('index'))

	@app.route('/admin/dashboard', methods = ['GET'])
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

	@app.route('/admin/organizations', methods = ['GET', 'POST'])
	@is_authorized
	def show_organizations():
		form = OrganizationForm()
		fields = [ form.name, form.csrf_token ]

		if form.validate_on_submit():
			new_organization = Organization(request.form['name'])
			db.session.add(new_organization)
			db.session.commit()
			return redirect(url_for('dashboard'))

		organizations = Organization.query.all()
		organization_list = [
			{
				'name': org.name,
                                'link': url_for('edit_organization', organization_id = org.id),
				'delete_link': url_for('delete_organization', organization_id = org.id)
			} for org in organizations
		]

		return render_template(
			'organizations.html',
			organizations = organization_list,
			fields = fields,
			form = form
		)

	@app.route('/admin/add-organization', methods = ['GET', 'POST'])
	@is_authorized
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
			return redirect(url_for('show_organizations'))

		return render_template(
			'organization_form.html',
			postback_url = url_for('add_organization'),
			form = form,
			title = 'Add Organization'
		)

	
	@app.route('/admin/delete-organization/<int:organization_id>', methods = ['POST'])
	@is_authorized
	def delete_organization(organization_id):
		organization = Organization.query.filter_by(id = organization_id).first()
		db.session.delete(organization)
		db.session.commit()
		return redirect(url_for('show_organizations'))

	@app.route('/admin/edit-organization/<int:organization_id>', methods = ['GET', 'POST'])
	@is_authorized
	def edit_organization(organization_id):
		organization = Organization.query.filter_by(id = organization_id).first()
		postback_url = url_for('edit_organization', organization_id = organization_id)

                current_categories = { c.id : True for c in organization.categories }

		if organization == None:
			return render_template('404.html')

		categories = Category.query.all()
		category_options = [{
			'description': c.name,
			'field_id': c.id,
			'checkbox': True if c.id in current_categories else False,
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


	@app.route('/admin/users', methods = ['GET'])
	@is_authorized
	def show_users():
		users = User.query.all()
		user_list = [ { 'name': u.username , 'link': url_for('edit_user', user_id = u.id) }
			for u in users ]
		return render_template('users.html', users = user_list)

	@app.route('/admin/add-user', methods = ['GET', 'POST'])
	@is_authorized
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
			return redirect(url_for('show_users'))

		return render_template(
			'user_form.html',
			title = 'Add User',
			form = form,
			postback_url = url_for('add_user')
		)


	@app.route('/admin/edit-user/<int:user_id>', methods = ['GET', 'POST'])
	@is_authorized
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
		postback_url = url_for('edit_user', user_id = user_id)

		form.organization.choices = BLANK_CHOICE + [ (o.id, o.name) for o in Organization.query.all() ]

		if form.validate_on_submit():
			user.username = form.username.data
			user.first_name = form.first_name.data
			user.last_name = form.last_name.data
			user.organization_id = None if form.organization.data == 0 else form.organization.data

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


	@app.route('/admin/categories')
	@is_authorized
	def show_categories():
		categories = [{
			'name': c.name,
			'link': url_for('edit_category', category_id = c.id),
		} for c in Category.query.all()]

		return render_template('categories.html', categories = categories)


	@app.route('/admin/add-category', methods = ['GET', 'POST'])
	@is_authorized
	def add_category():
		form = CategoryForm()

		if form.validate_on_submit():
			category = Category(form.name.data)
			db.session.add(category)
			db.session.commit()
			return redirect(url_for('show_categories'))

		return render_template(
			'category_form.html',
			title = 'Add Category',
			form = form,
			postback_url = url_for('add_category')
		)


	@app.route('/admin/edit-category/<int:category_id>', methods = ['GET', 'POST'])
	@is_authorized
	def edit_category(category_id):
		form = CategoryForm()
		category = Category.query.filter_by(id = category_id).first()
                postback_url = url_for('edit_category', category_id = category_id)

		if form.validate_on_submit():
			category.name = form.name.data
			db.session.commit()
			return redirect(url_for('show_categories'))


		form.name.data = category.name
		return render_template(
			'category_form.html',
			title = 'Edit Category',
			form = form,
			postback_url = postback_url
		)


	@app.route('/admin/products')
	@is_authorized
	def show_products():
		products = [ { 'name': p.name, 'link': url_for('edit_product', product_id = p.id) }
			for p in Product.query.all()]
		return render_template('products.html', products = products)

	@app.route('/admin/add-product', methods = ['GET', 'POST'])
	@is_authorized
	def add_product():
		form = ProductForm()
		form.category.choices = [ (c.id, c.name) for c in Category.query.all() ]

		if form.validate_on_submit():
			product = Product(form.name.data, form.category.data)
			db.session.add(product)
			db.session.commit()
			return redirect(url_for('show_products'))

		return render_template(
			'product_form.html',
			title = 'Add Product',
			form = form,
			postback_url = url_for('add_product')
		)


	@app.route('/admin/edit-product/<int:product_id>', methods = ['GET', 'POST'])
	@is_authorized
	def edit_product(product_id):
		form = ProductForm()
		form.category.choices = [ (c.id, c.name) for c in Category.query.all() ]
		product = Product.query.filter_by(id = product_id).first()
                postback_url = url_for('edit_product', product_id = product_id)

		if form.validate_on_submit():
			product.name = form.name.data
			product.category_id = form.category.data
			db.session.commit()
			return redirect(url_for('show_products'))

		form.name.data = product.name
		form.category.data = product.category_id

		return render_template(
			'product_form.html',
			title = 'Edit Product',
			form = form,
			postback_url = postback_url
		)

	@app.route('/admin/permissions')
	@is_authorized
	def show_permissions():
		permissions = [	{ 'name': p.description } for p in Permission.query.all() ]
		return render_template('permissions.html', permissions = permissions)

