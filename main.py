from flask import Flask, render_template, url_for
from flask_assets import Environment, Bundle
# sqlalchemy connection
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item
app = Flask(__name__)

assets = Environment(app)
assets.url = app.static_url_path
assets.directory = app.static_folder
assets.append_path('sass')
# Bundle SASS files
scss = Bundle('_main.scss', filters='pyscss', output='css/all.css')
assets.register('scss_all', scss)

engine = create_engine('sqlite:///categoryitem.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()

@app.route('/')
def home():
	return render_template("home.html")

@app.route('/categories')
def getAllCategories():
	categories = session.query(Category).all()
	return render_template('allcategories.html', categories = categories)

if __name__ == "__main__":
	app.debug = True
	app.run("127.0.0.1", port = 8080)
