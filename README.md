Categorize.Me
=============

**Description**: An item cataloging app complete with authentication and CRUD functionality.

---


screenshots:
![home1](https://cloud.githubusercontent.com/assets/11083531/17197495/2a215de4-543b-11e6-81b3-e74533a096f3.png)

![app1](https://cloud.githubusercontent.com/assets/11083531/17197498/2f48a53e-543b-11e6-8a69-065c19b95b54.png)


---


Requirements:
------------

1. Python (installed on your machine or VM)
2. [pip](https://pypi.python.org/pypi/pip) (package manager for python)
3. [Flask](http://flask.pocoo.org/) (micro-framework for Python)
  * Unix install with: `pip install Flask`
5. [Flask-Assets](https://flask-assets.readthedocs.io/en/latest/) (Flask-Assets helps you to integrate webassets into your Flask application)	
6.  [SQLite](https://www.sqlite.org/) (SQLite3 is an extremely lightweight SQL database engine that is self-contained and serverless)
7. [SQLAlchemy](http://www.sqlalchemy.org/) (Python SQL toolkit and ORM)



Installation:
-------------

1. Clone this repo: `https://github.com/vinnyA3/item-catalog.git`
2. Install all necessary requirements (see above ^)
3. Initialize the database: `python database_setup.py`
4. (Optional) Populate the database with default data: `python filldatabase.py`
  * Note: you can skip this step and populate with your own data in the application
5. Start the application: `python main.py`
6. Navigate to: <http://localhost:8080/>
  * Note: Make sure there are no other processes running on port 8080, otherwise change the port number at the end of main.py
7. Play around and have fun!


**Note:** If you edit the app styles, do so in the sass folder.  You can write normal css.  Also, do not edit the client_secret.json file!



API:
----

This application contains an API endpoint that will return a JSON object containing all the items in the database

endpoint:  `/items/all/JSON`
