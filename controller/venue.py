
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from app import app
from models import *
from helper import *
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

#  ----------------------------------------------------------------
#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    locations = get_distinct_locations_with_venues()
    data = build_location_data_with_venues(locations)
    return render_template('pages/venues.html', areas=data)

def get_distinct_locations_with_venues():
    return Venue.query.distinct(Venue.city, Venue.state).order_by(Venue.state, Venue.city).all()

def build_location_data_with_venues(locations):
    def get_venues_data(location):
        venues_data = []
        venues = Venue.query.filter_by(city=location.city, state=location.state).all()
        for venue in venues:
            num_upcoming_shows = get_upcoming_shows_count(venue)
            venues_data.append({
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': num_upcoming_shows
            })
        return venues_data
    
    return [{
        'city': location.city,
        'state': location.state,
        'venues': get_venues_data(location)
    } for location in locations]

def get_upcoming_shows_count(venue):
    return Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > datetime.now()).count()

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    venue_results = search_venues_by_name(search_term)
    data = build_venue_data_with_upcoming_shows_count(venue_results)
    response = {
        "count": len(venue_results),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)

def search_venues_by_name(search_term):
    return Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

def build_venue_data_with_upcoming_shows_count(venues):
    def get_upcoming_shows_count(venue):
        return Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > datetime.now()).count()

    return [{
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": get_upcoming_shows_count(venue)
    } for venue in venues]

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    now = datetime.now()
    
    past_shows = get_shows(venue_id, now, '<')
    upcoming_shows = get_shows(venue_id, now, '>=')
    
    data = {
        'id': venue.id,
        'name': venue.name,
        'genres': venue.genres,
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'website': venue.website_link,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link,
        'past_shows': format_shows(past_shows),
        'upcoming_shows': format_shows(upcoming_shows),
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows),
    }
    return render_template('pages/show_venue.html', venue=data)

def get_shows(venue_id, now, operator):
    return db.session.query(Show).join(Artist).filter(
        Show.venue_id == venue_id,
        eval(f"Show.start_time {operator} now")
    ).all()

def format_shows(shows):
    return [
        {
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            'start_time': show.start_time.isoformat()
        }
        for show in shows
    ]

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
      form = VenueForm(request.form, meta={'csrf': False})

      if form.validate_on_submit:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        address = request.form.get('address')
        phone = request.form.get('phone')
        genres = request.form.getlist('genres')
        facebook_link = request.form.get('facebook_link')
        image_link = request.form.get('image_link')
        website_link = request.form.get('website_link')
        seeking_talent = request.form.get('seeking_talent')

        if seeking_talent == 'y':
          seeking_talent = 1
        else:
          seeking_talent = 0
        seeking_description = request.form.get('seeking_description')

        venue = Venue(name=name,
                      city=city,
                      state=state, 
                      phone=phone,
                      address=address,
                      genres=genres,
                      facebook_link=facebook_link,
                      image_link=image_link,
                      website_link=website_link,
                      seeking_description=seeking_description)
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')
    except Exception as e:
       print("Error: ", e)
       db.session.rollback()
    finally:
       db.session.close()
    return render_template('forms/new_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first()

  if venue is None:
     abort(404)

  data = {
      'id': venue.id,
      'name': venue.name,
      'genres': venue.genres,
      'address': venue.address,
      'city': venue.city,
      'state': venue.state,
      'phone': venue.phone,
      'website_link': venue.website_link,
      'facebook_link': venue.facebook_link,
      'seeking_talent': venue.seeking_talent,
      'seeking_description': venue.seeking_description,
      'image_link': venue.image_link
  }
  form = VenueForm(formdata=request.form if request.method == 'POST' else None, data=data)
  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.filter_by(id=venue_id).first()
  if venue is None:
     abort(404)

  form = VenueForm(request.form)

  if form.validate_on_submit():
    venue.name = form.name.data
    venue.genres = request.form.getlist('genres')
    venue.address = form.address.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.website_link = form.website_link.data
    venue.facebook_link = form.facebook_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    venue.image_link = form.image_link.data
    db.session.add(venue)
    db.session.commit()
    return redirect(url_for('show_venue', venue_id=venue_id))
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  venue = Venue.query.filter_by(id=venue_id).first()

  if venue is None:
     abort(404)

  try:
     db.session.delete(venue)
     db.session.commit()
     flash(f"Venue {venue.name} has delete successfully!!", 'success')
     return redirect(url_for('index'))
  except Exception as e:
     logger.exception(f'Delete {venue.name} is errors!', exc_info=True, stacklevel=True)
     flash(f'Venue {venue.name} cant not deleted!!.', 'danger')
