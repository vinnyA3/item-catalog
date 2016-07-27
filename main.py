from flask import Flask, render_template, url_for, request, redirect, flash
from flask_assets import Environment, Bundle
# sqlalchemy connection
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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

# google authentication -> login


@app.route('/')
def home():
	return render_template("home.html")

@app.route('/categories/')
def getAllCategories():
	categories = session.query(Category).all()
	return render_template('allcategories.html', categories = categories)

@app.route('/categories/<int:category_id>/')
def getSpecificCategory(category_id):
	categories = session.query(Category).all()
	queried_category = session.query(Category).filter_by(id=category_id).one()
	queried_category_items = session.query(Item).filter_by(
		category_id=queried_category.id).all()
	return render_template('allcategories.html', categories=categories,
					queried_category=queried_category,
					queried_category_items=queried_category_items)

@app.route('/categories/<int:category_id>/<int:item_id>/')
def getItem(category_id, item_id):
	print item_id
	item = session.query(Item).filter_by(id=item_id).one()
	return render_template('categoryitem.html', item=item,
						category_id=category_id)

@app.route('/categories/<int:category_id>/new',
			methods=['GET', 'POST'])
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
			return redirect('getSpecificCategory', category_id=category_id)
	else:
		return render_template(url_for('newitem.html', category_id=category_id))

@app.route('/categories/<int:category_id>/<int:item_id>/edit',
			methods=['GET','POST'])
def editItem(category_id, item_id):
	# get the edited item info
	edit_item = session.query(Item).filter_by(id=item_id).one()
	if request.method == 'POST':
		edit_name = request.form['name'] if request.form['name'] != '' else edit_item.name
		edit_desc = request.form['description'] if request.form['description'] != '' else edit_item.description

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
		return redirect('getSpecificCategory', category_id=category_id)
	else:
		return render_template('deleteitem.html', category_id=category_id,
							item=item)


if __name__ == "__main__":
	app.secret_key = 'pokemongohastakenovertheworld'
	app.debug = True
	app.run("127.0.0.1", port = 8080)
