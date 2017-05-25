from __future__ import print_function
import sys
from flask import render_template, request, session, redirect
from database import db
from models import User, Organization
from main import app
from middleware import is_authorized
from forms import NewOrganizationForm, AddUserForm, EditUserForm

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
			db.session.add(new_user)
			db.session.commit()
			return redirect('/users')

		return render_template('add_user.html', fields = fields)


	@app.route('/edit-user/<int:user_id>', methods = ['GET', 'POST'])
	def edit_user(user_id):
		data_in = { 'organizations': [ o.name for o in Organization.query.order_by('name').all() ] }
		form = EditUserForm(data = data_in)
		fields = [
			form.username,
			form.password,
			form.csrf_token,
			form.first_name,
			form.last_name,
			form.organizations,
		]

		if form.validate_on_submit():
			updates = {}
			updates['username'] = form.username.data
			updates['first_name'] = form.first_name.data
			updates['last_name'] = form.last_name.data

			if form.password.data != '':
				updates['password'] = form.password.data

			User.query.filter_by(id = user_id).update(updates)

			db.session.commit()
			return redirect('/users')

		user = User.query.filter_by(id = user_id).first()
		form.username.data = user.username
		form.password.data = user.password
		form.first_name.data = user.first_name
		form.last_name.data = user.last_name

		return render_template(
			'edit_user.html',
			fields = fields,
			postback_url = postback_url
		)