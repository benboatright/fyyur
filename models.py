# Used JULIANO's framework to set up this file
#6/20/22 # https://knowledge.udacity.com/questions/389683

from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from forms import *
from flask_migrate import Migrate


# set up app,db, and migrate in this models.py file
app = Flask(__name__)
# REVIEW CHANGE 1: moved the config code below to from app.py to models.py to fix the table creation issue.
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db) #from todolistapp code from Amy Hua

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False) #these are required in the forms.py file
    city = db.Column(db.String(120),nullable=False) #these are required in the forms.py file
    state = db.Column(db.String(120),nullable=False) #these are required in the forms.py file
    address = db.Column(db.String(120)) #these are required in the forms.py file
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String)) #Hold the genres in an Array #6/18/22 #https://docs.sqlalchemy.org/en/14/core/type_basics.html #Lucian's comment #https://stackoverflow.com/questions/14219775/update-a-postgresql-array-using-sqlalchemy
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean,nullable=False,default=False) #Set default to False #6/18/22 #https://docs.sqlalchemy.org/en/14/core/defaults.html#scalar-defaults
    seeking_description = db.Column(db.String(500))

    # COMPLETE: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False) #these are required in the forms.py file
    city = db.Column(db.String(120),nullable=False) #these are required in the forms.py file
    state = db.Column(db.String(120),nullable=False) #these are required in the forms.py file
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String)) #Hold the genres in an Array #6/18/22 #https://docs.sqlalchemy.org/en/14/core/type_basics.html #lucian's comment #https://stackoverflow.com/questions/14219775/update-a-postgresql-array-using-sqlalchemy
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean,nullable=False,default=False) #Set default to False #6/18/22 #https://docs.sqlalchemy.org/en/14/core/defaults.html#scalar-defaults
    seeking_description = db.Column(db.String(500))

    # COMPLETE: implement any missing fields, as a database migration using Flask-Migrate

# COMPLETE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ ='Show'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id')) #Using foriegn key to relate show to artist #6/18/22 #https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/
  venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id')) #using foriegn key to relate show to venue #6/18/22 #https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/
  start_time = db.Column(db.DateTime,nullable=False) #using DateTime data type #6/18/22 #https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/#quickstart
