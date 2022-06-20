#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import ForeignKey
from forms import *
import sys
from flask_migrate import Migrate
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
# pull the models info from the models.py
from models import app,db,Show,Artist,Venue

moment = Moment(app)



# COMPLETE: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # COMPLETE: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  # get all the city and state combinations
  city_state_combos = Venue.query.distinct(Venue.city,Venue.state).all() #6/18/22 # get distinct values #https://devsheet.com/code-snippet/sqlalchemy-query-to-get-distinct-records-from-table/
  # initialize the data list
  data = []
  #loop through all the city state combinations
  for city_state in city_state_combos:
    # find all the venues in the given city state combination
    venues = Venue.query.filter_by(city=city_state.city).filter_by(state=city_state.state) #6/18/22 #filter_by #https://docs.sqlalchemy.org/en/14/orm/query.html
    #initialize the venue_data list
    venue_data =[]
    #for each venue in the given city state combination, find the id, name, and number of upcoming shows for each venue and append the data to the venue_data list
    for venue in venues:
      num_upcoming_shows = Show.query.filter_by(venue_id=venue.id).filter(Show.start_time>datetime.datetime.now()).count() #used "filter" instead of "filter_by" in the second filter #David Johnstone #https://stackoverflow.com/questions/3332991/sqlalchemy-filter-multiple-columns #6/18/22 #get current date #https://stackoverflow.com/questions/415511/how-do-i-get-the-current-time
      venue_data.append({
        "id":venue.id,
        "name":venue.name,
        "num_coming_shows":num_upcoming_shows
      })
    # append the city state combination data with the venues to the data list
    data.append({
      "city":city_state.city,
      "state":city_state.state,
      "venues": venue_data
    })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # COMPLETE: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # get the search term
  search_term=request.form.get('search_term','')
  # filter the venues that include the search term
  venue_list = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all() #6/19/22 #use ilike to #https://docs.sqlalchemy.org/en/14/orm/internals.html?highlight=ilike#sqlalchemy.orm.attributes.QueryableAttribute.ilike #https://stackoverflow.com/questions/20363836/postgresql-ilike-query-with-sqlalchemy
  # initialize the data list
  data=[]
  # for each venue, append the venue id, name, and number of shows to the data list
  for venue in venue_list:
    data.append({
      "id":venue.id,
      "name":venue.name,
      "num_upcoming_shows":Show.query.filter_by(venue_id=venue.id).filter(Show.start_time>datetime.datetime.now()).count() #used "filter" instead of "filter_by" in the second filter #David Johnstone #https://stackoverflow.com/questions/3332991/sqlalchemy-filter-multiple-columns #6/18/22 #get current date #https://stackoverflow.com/questions/415511/how-do-i-get-the-current-time
    })
  # use the length of the venue list to show the number of search results and populate with the data list
  response={
    "count":len(venue_list),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # COMPLETE: replace with real venue data from the venues table, using venue_id
  # get the venue data based on venue_id
  venue_data = Venue.query.get(venue_id)
  # find the past shows filtered by the venue_id and start time
  # REVIEW CHANGE 1: review recommended changing to JOIN. I changed my code using the code that they suggested. I am not sure who the reviewer was to properly attribute this to.
  past_shows = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_data.id).filter(Show.start_time<=datetime.datetime.now()).all() #used "filter" instead of "filter_by" in the second filter #David Johnstone #https://stackoverflow.com/questions/3332991/sqlalchemy-filter-multiple-columns #6/18/22 #get current date #https://stackoverflow.com/questions/415511/how-do-i-get-the-current-time
  # initialize past_show_list
  past_show_list = []
  # loop through the past shows and store the artist/show information as a dictionary in new list
  for show in past_shows:
    artist_data = Artist.query.get(show.artist_id)
    past_show_list.append({
      "artist_id":artist_data.id,
      "artist_name":artist_data.name,
      "artist_image_link":artist_data.image_link,
      "start_time": str(show.start_time)
    })

  # find the future shows filtered by the venue_id and start time
  # REVIEW CHANGE 1: review recommended changing to JOIN. I changed my code using the code that they suggested. I am not sure who the reviewer was to properly attribute this to.
  future_shows = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_data.id).filter(Show.start_time>datetime.datetime.now()).all() #6/18/22 #get current date #https://stackoverflow.com/questions/415511/how-do-i-get-the-current-time #used "filter" instead of "filter_by" in the second filter #https://stackoverflow.com/questions/3332991/sqlalchemy-filter-multiple-columns
  # initialize future_show_list
  future_show_list = []
  # loop through the future shows and store the artist/show information as a dictionary in a new list
  for show in future_shows:
    artist_data = Artist.query.get(show.artist_id)
    future_show_list.append({
      "artist_id":artist_data.id,
      "artist_name":artist_data.name,
      "artist_image_link":artist_data.image_link,
      "start_time":str(show.start_time)
    }) 

  # store the venue data, past and future show and artist data, and the counts in the dictionay below
  data={
    "id":venue_id,
    "name":venue_data.name,
    "genres":venue_data.genres,
    "address":venue_data.address,
    "city":venue_data.city,
    "state":venue_data.state,
    "phone":venue_data.phone,
    "website": venue_data.website_link,
    "facebook_link": venue_data.facebook_link,
    "seeking_talent":venue_data.seeking_talent,
    "seeking_description":venue_data.seeking_description,
    "image_link":venue_data.image_link,
    "past_shows": past_show_list,
    "upcoming_shows": future_show_list,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(future_shows)
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # COMPLETE: insert form data as a new Venue record in the db, instead
  # COMPLETE: modify data to be the data object returned from db insertion

  ### References that guided this function
    #6/18/22 #Documentation guide for setting up the function #https://flask.palletsprojects.com/en/2.1.x/patterns/wtforms/
    #6/18/22 #the try,except, and finally instructions from the todoapplist sample from Amy Hua # When I had the error and body in the code it did not work
  # get the request form
  form = VenueForm(request.form)
  # check if the form is valid
  if form.validate():
    # attempt to upload the data to the Venue table
    try:
      #create a Venue record out of the local variables
      venue = Venue(name=form.name.data,
                    city=form.city.data,
                    state=form.state.data,
                    address=form.address.data,
                    phone=form.phone.data,
                    image_link=form.image_link.data,
                    genres=form.genres.data,
                    facebook_link=form.facebook_link.data,
                    website_link=form.website_link.data,
                    seeking_talent=form.seeking_talent.data,
                    seeking_description=form.seeking_description.data)

      #add and commit the record
      db.session.add(venue)
      db.session.commit()
  
      # on successful db insert, flash success
      flash('Venue ' + form.name.data + ' was successfully listed!')
    # rollback the table commit if the data could not be uploaded
    except:
      db.session.rollback()
      print(sys.exc_info)
    finally:
      db.session.close()
  else:
    # COMPLETE: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html',form=form)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # Used the try, except, finally framework from Amy Hua
  try:
    #delete the venue_id
    Venue.query.filter_by(id=venue_id).delete() #6/20/22 #Used adarsh comment to find the .delete() method #https://stackoverflow.com/questions/27158573/how-to-delete-a-record-by-id-in-flask-sqlalchemy
    #commit the changes
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_infor)
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # COMPLETE: replace with real data returned from querying the database
  # initalize the data list
  data = []
  # find all the artists
  artist_list = Artist.query.all()
  # for each artist, append the artist's id and name to the data list
  for artist in artist_list:
    data.append({
      "id":artist.id,
      "name":artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # COMPLETE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # get the search keyword
  search_term=request.form.get('search_term', '')
  # filter all the artist based on the search term
  artist_list = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all() #6/19/22 #use ilike to #https://docs.sqlalchemy.org/en/14/orm/internals.html?highlight=ilike#sqlalchemy.orm.attributes.QueryableAttribute.ilike #https://stackoverflow.com/questions/20363836/postgresql-ilike-query-with-sqlalchemy
  # initialize the data list
  data=[]
  # for each artist found in the artist list, append the id, name and number of upcoming shows
  for artist in artist_list:
    data.append({
      "id":artist.id,
      "name":artist.name,
      "num_upcoming_shows":Show.query.filter_by(artist_id=artist.id).filter(Show.start_time>datetime.datetime.now()).count() #used "filter" instead of "filter_by" in the second filter #David Johnstone #https://stackoverflow.com/questions/3332991/sqlalchemy-filter-multiple-columns #6/18/22 #get current date #https://stackoverflow.com/questions/415511/how-do-i-get-the-current-time
    })
  # add the count of search resulsts by using the length of the artist list and add the data list
  response = {
    "count":len(artist_list),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # COMPLETE: replace with real artist data from the artist table, using artist_id
  # get artist data based on artist_id
  artist_data = Artist.query.get(artist_id)
  # get the past shows filtered by artist id and start time
  # REVIEW CHANGE 1: review recommended changing to JOIN. I changed my code using the code that they suggested. I am not sure who the reviewer was to properly attribute this to.
  past_shows = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_data.id).filter(Show.start_time<=datetime.datetime.now()).all() #used "filter" instead of "filter_by" in the second filter #David Johnstone #https://stackoverflow.com/questions/3332991/sqlalchemy-filter-multiple-columns #6/18/22 #get current date #https://stackoverflow.com/questions/415511/how-do-i-get-the-current-time
  # initialize past_show_list
  past_show_list = []
  # loop through artist's last shows and append the venue/show data to the past_show_list
  for show in past_shows:
    venue_data = Venue.query.get(show.venue_id)
    past_show_list.append({
      "veunue_id":venue_data.id,
      "venue_name":venue_data.name,
      "venue_image_link":venue_data.image_link,
      "start_time":str(show.start_time)
    })

  # get the future shows filtered by artist id and start time
  # REVIEW CHANGE 1: review recommended changing to JOIN. I changed my code using the code that they suggested. I am not sure who the reviewer was to properly attribute this code to.
  future_shows = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_data.id).filter(Show.start_time>datetime.datetime.now()).all() #used "filter" instead of "filter_by" in the second filter #David Johnstone #https://stackoverflow.com/questions/3332991/sqlalchemy-filter-multiple-columns #6/18/22 #get current date #https://stackoverflow.com/questions/415511/how-do-i-get-the-current-time
  #initalize the future_show_list
  future_show_list = []
  #loop through artist's future shows and append the venue/show data to the future_show_list
  for show in future_shows:
    venue_data = Venue.query.get(show.venue_id)
    future_show_list.append({
      "venue_id":venue_data.id,
      "venue_name":venue_data.name,
      "venue_image_link":venue_data.image_link,
      "start_time":str(show.start_time)
    })

  # use the artist data, the past and future show lists, and the length of the past and future shows queries to fill in the dictionary
  data={
    "id":artist_id,
    "name":artist_data.name,
    "genres":artist_data.genres,
    "city":artist_data.city,
    "state":artist_data.state,
    "phone":artist_data.phone,
    "website":artist_data.website_link,
    "facebook_link":artist_data.facebook_link,
    "seeking_venue":artist_data.seeking_venue,
    "seeking_description":artist_data.seeking_description,
    "image_link":artist_data.image_link,
    "past_shows":past_show_list,
    "upcoming_shows":future_show_list,
    "past_shows_count":len(past_shows),
    "upcoming_shows_count":len(future_shows)
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  ### References
  # 6/19/22 used the documentation to learn the "populate_obj" method #https://wtforms.readthedocs.io/en/2.3.x/forms/
  # get the artist data from the Artist table using the artist_id
  artist = Artist.query.get(artist_id)
  # connect the form and set object the artist queried above 
  form = ArtistForm(obj=artist)
  # populate the form
  form.populate_obj(artist) 
  # COMPLETE: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # COMPLETE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  # get the form requests from the Artist form
  form = ArtistForm(request.form)
  # get the right artist record from the artist table
  artist = Artist.query.get(artist_id)
  # update the artist's info based on the form edits
  artist.name = form.name.data
  artist.city = form.city.data
  artist.state = form.state.data
  artist.phone = form.phone.data
  artist.genres = form.genres.data
  artist.facebook_link = form.facebook_link.data
  artist.image_link = form.image_link.data
  artist.website_link = form.website_link.data
  artist.seeking_venue = form.seeking_venue.data
  artist.seeking_description = form.seeking_description.data
  # commit the changes
  db.session.commit()
  return redirect(url_for('show_artist', form=form, artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # get the venue data from the venue table based on venue id
  venue = Venue.query.get(venue_id)
  # connect the form useing the venue queried previously
  form = VenueForm(obj=venue)
  # populate the venue data in the form
  form.populate_obj(venue)
  # COMPLETE: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # COMPLETE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  # connect the form
  form = VenueForm(request.form)
  # get the specific venue from the venue table
  venue = Venue.query.get(venue_id)
  # updata the venue record with changes from the form
  venue.name = form.name.data
  venue.city = form.city.data
  venue.state = form.state.data
  venue.address = form.address.data
  venue.phone = form.phone.data
  venue.genres = form.genres.data
  venue.facebook_link = form.facebook_link.data
  venue.image_link = form.image_link.data
  venue.website_link = form.website_link.data
  venue.seeking_talent = form.seeking_talent.data
  venue.seeking_descriptiton = form.seeking_description.data
  # commit the changes to the table
  db.session.commit()
  return redirect(url_for('show_venue', form=form,venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # COMPLETE: insert form data as a new Venue record in the db, instead
  # COMPLETE: modify data to be the data object returned from db insertion
  ### References that guided this function
    #6/18/22 #Documentation guide for setting up the function #https://flask.palletsprojects.com/en/2.1.x/patterns/wtforms/
    #6/18/22 #the try,except, and finally instructions from the todoapplist sample from Amy Hua # When I had the error and body in the code it did not work
  # get the artist data from the form
  form = ArtistForm(request.form)
  # check if the form data is valid
  if form.validate():
    # try to upload the form data to the Artist table
    try:
      # create a new record in the Artist table from the form data submitted
      artist = Artist(name=form.name.data,
                      city=form.city.data,
                      state=form.state.data,
                      phone=form.phone.data,
                      image_link=form.image_link.data,
                      genres=form.genres.data,
                      facebook_link=form.facebook_link.data,
                      website_link=form.website_link.data,
                      seeking_venue=form.seeking_venue.data,
                      seeking_description=form.seeking_description.data)

      #add and commit the data from the form
      db.session.add(artist)
      db.session.commit()

      # on successful db insert, flash success
      flash('Artist ' + form.name.data + ' was successfully listed!')
    # roll back the commit if the new record could not be uploaded
    except:
      db.session.rollback()
      print(sys.exc_info)
    finally:
      db.session.close()
  else:
    # COMPLETE: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
  return render_template('pages/home.html',form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  #displays list of shows at /shows
  #COMPLETE: replace with real venues data.
  # initialize the data list
  data=[]
  # find all the shows
  show_list = Show.query.all()
  # for each show, find the venue data and artist data associated with the foreign keys and append the data to the data list
  for show in show_list:
    venue_data = Venue.query.get(show.venue_id)
    artist_data = Artist.query.get(show.artist_id)
    data.append({
      "venue_id":show.venue_id,
      "venue_name":venue_data.name,
      "artist_id":show.artist_id,
      "artist_name":artist_data.name,
      "artist_image_link":artist_data.image_link,
      "start_time":str(show.start_time)
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # COMPLETE: insert form data as a new Show record in the db, instead
  # Based on Amy Hua's try, except, finally framework from the course
  form = ShowForm(request.form)
  #check if form is valid
  if form.validate():
    # try to add the record to the Show table
    try:
      show = Show(artist_id=form.artist_id.data,
                  venue_id=form.venue_id.data,
                  start_time=form.start_time.data)
      
      db.session.add(show)
      db.session.commit()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
    except:
      db.session.rollback()
      print(sys.exc_info)
    finally:
      db.session.close()
  else:
    # COMPLETE: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html',form=form)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
