from flask import render_template, request, session, redirect
from models import User
from main import app
from middleware import is_authorized

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
		return render_template('dashboard.html')
