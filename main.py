from flask import Flask, render_template, url_for, request, redirect, flash, \
jsonify
from flask_assets import Environment, Bundle
# sqlalchemy connection
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from database_setup import Base, Category, Item

# new imports
from flask import session as login_session
import random, string

# imports for OAuth
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# declare client id by referenceing client secrets file
CLIENT_ID = json.loads(
	open('client_secret.json', 'r').read())['web']['client_id']

# initialize app
app = Flask(__name__)

assets = Environment(app)
assets.url = app.static_url_path
assets.directory = app.static_folder
assets.append_path('sass')
# Bundle SASS files
scss = Bundle('_main.scss', filters='pyscss', output='css/all.css',
				depends=('**/*.scss'))
assets.register('scss_all', scss)

engine = create_engine('sqlite:///categoryitem.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()

# context processor to allow all our templates know if we are logged in or not
@app.context_processor
def provide_login_status():
	if 'username' in login_session:
		return dict(isLoggedIn=True)
	else:
		# create state token to prevent request forgery
		# Store it in the session for later validation
		state = ''.join(random.choice(string.ascii_uppercase + string.digits) \
						for x in range(32))
		login_session['state'] = state
		# the user is logged in, lets let the templates know
		return dict(isLoggedIn=False, STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():

	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameters'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	code = request.data

	try:
		# upgrade the authorization code into a credentials object
		oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		response = make_response(json.dumps('Failed to upgrade auth code'),
							401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# check that the access token is valid
	# debug
	# print credentials.access_token
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' \
		% access_token)

	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])
	# if there was an error in the access token info, abort mission!
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		reponse.headers['Content-Type'] = 'application/json'

	# verify that the access token is used for intended use
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(
			json.dumps("Token's user ID does not match given user ID.", 401))
		response.headers['Content-Type'] = 'application/json'
		return response
	# Verify that the access token is valid for this application
	if result['issued_to'] != CLIENT_ID:
		response = make_response(
			json.dumps("Token's client id does not match the application"))
		response.headers['Content-Type'] = 'application/json'
		return response
	# check to see if the user is already logged in
	stored_credentials = login_session.get('credentials')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_credentials is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is logged in'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Store the access token in the session for later use
	login_session['credentials'] = credentials.access_token
	login_session['gplus_id'] = gplus_id

	# get the user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()

	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']

	print "done!"
	return "Great!"

# DISCONNECT - revoke current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
	# only disconnect a connected user
	access_token = login_session['credentials']

	if access_token is None:
		response = make_response(json.dumps('Current user not connected', 401))
		response.headers['Content-Type'] = 'application/json'
		return response
	# Execute HTTP GET request to revoke the current token
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]
	print "result is: "
	print result

	if result['status'] == '200':
		# reset the user's session
		del login_session['credentials']
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']
		response = make_response(json.dumps('Successfully disconnected.'), 200)
		# response.headers['Content-Type'] = 'application/json'
		# debug
		print response
		# print response
		flash('Successfully Logged Out')
		return redirect(url_for('getAllCategories'))

	else:
		response = make_response(json.dumps('Failed to revoke user token'), 400)
		response.headers['Content-Type'] = 'application/json'
		return response

# API Endpoint: get all items
@app.route('/items/all/JSON')
def getAllItemsJSON():
	items = session.query(Item).all()
	return jsonify(Items = [i.serialize for i in items])


@app.route('/')
def home():
	return render_template("home.html")


@app.route('/categories/')
def getAllCategories():
	categories = session.query(Category).all()
	# get the latest items
	latest_items = session.query(Item).order_by(Item.id.desc())\
	.join("category").all()
	# debug
	# for i in latest_items:
	#	print i.category.name
	return render_template('allcategories.html', categories = categories,
						latest_items=latest_items)


@app.route('/categories/<int:category_id>/')
def getSpecificCategory(category_id):
	# set loggedIn variable to test if the user is logged in
	loggedIn = False

	if 'username' in login_session:
		# The user is logged in
		loggedIn = True

	categories = session.query(Category).all()
	queried_category = session.query(Category).filter_by(id=category_id).one()
	queried_category_items = session.query(Item).filter_by(
		category_id=queried_category.id).all()

	return render_template('allcategories.html', categories=categories,
					queried_category=queried_category,
					queried_category_items=queried_category_items,
					loggedIn=loggedIn)


@app.route('/categories/new',methods=['GET','POST'])
def addNewCategory():
	if request.method == 'POST':
		if request.form['name'] != '':
			# create a new item
			newCategory = Category(name=request.form['name'])
			session.add(newCategory)
			session.commit()
			flash('Category has been added!')
			return redirect('getAllCategories')
	else:
		return render_template('newcategory.html')


@app.route('/categories/<int:category_id>/<int:item_id>/')
def getItem(category_id, item_id):
	# set loggedIn variable to test if the user is logged in
	loggedIn = False

	if 'username' in login_session:
		# The user is logged in
		loggedIn = True

	item = session.query(Item).filter_by(id=item_id).one()
	return render_template('categoryitem.html', item=item,
						category_id=category_id, loggedIn = loggedIn)


@app.route('/categories/<int:category_id>/new',methods=['GET','POST'])
def newItem(category_id):
	if request.method == 'POST':
		if request.form['name'] != '':
			# create a new item
			newItem = Item(name=request.form['name'],
					description=request.form['description'],
					category_id=category_id)
			session.add(newItem)
			session.commit()
			flash('Item has been added!')
			return redirect(url_for('getSpecificCategory',
							category_id=category_id))
	else:
		return render_template('newitem.html', category_id=category_id)


@app.route('/categories/<int:category_id>/<int:item_id>/edit',
			methods=['GET','POST'])
def editItem(category_id, item_id):
	# get the edited item info
	edit_item = session.query(Item).filter_by(id=item_id).one()
	if request.method == 'POST':
		edit_name = request.form['name'] \
		if request.form['name'] != '' else edit_item.name

		edit_desc = request.form['description'] \
		if request.form['description'] != '' else edit_item.description

		edit_item.name = edit_name
		edit_item.description = edit_desc

		session.add(edit_item)
		session.commit()
		flash('Item edited successfully!')
		return redirect(url_for('getItem', category_id=category_id,
							item_id=item_id))

	item = session.query(Item).filter_by(id=item_id).one()
	return render_template('edititem.html', item=item, category_id=category_id)


@app.route('/categories/<int:category_id>/<int:item_id>/delete',
			methods=['GET','POST'])
def deleteItem(category_id, item_id):
	# get the item
	item = session.query(Item).filter_by(id=item_id).one()
	if request.method == 'POST':
		session.delete(item)
		session.commit()
		flash('Item has been deleted!')
		return redirect(url_for('getSpecificCategory', category_id=category_id))
	else:
		return render_template('deleteitem.html', category_id=category_id,
							item=item)


if __name__ == "__main__":
	app.secret_key = 'pokemongohastakenovertheworld'
	app.debug = True
	app.run("127.0.0.1", port = 8080)
