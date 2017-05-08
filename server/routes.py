from flask import render_template
from main import app

def apply_routes(app):

	@app.route('/', methods = ['GET'])
	def index():
		return render_template('index.html')