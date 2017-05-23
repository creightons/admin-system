from __future__ import print_function
import sys
from flask import render_template, request, session, redirect
from database import db
from models import User, Organization
from main import app
from middleware import is_authorized
from forms import NewOrganizationForm

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
		organization_list = [ { 'name': org.name, 'link': '/edit-organization/' + str(org.id) }
			for org in organizations ]

		return render_template(
			'organizations.html',
			organizations = organization_list,
			fields = fields,
			form = form
		)

	@app.route('/add-organization', methods=['GET', 'POST'])
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