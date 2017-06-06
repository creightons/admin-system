from flask import session, redirect
from functools import wraps

def is_authorized(func):
	@wraps(func)

	def decorated_function(*args, **kwargs):
		if 'username' not in session:
			return redirect('/')

		return func(*args, **kwargs)

	return decorated_function
