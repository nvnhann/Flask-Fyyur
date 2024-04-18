
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from app import app
from helper import VenueForm
from models import *
from collections import defaultdict
import logging
logger = logging.getLogger(__name__)
#  ----------------------------------------------------------------
#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venues = Venue.query.all()
  grouped_venues = defaultdict(list)

  for venue in venues:
    grouped_venues[(venue.city, venue.state)].append(venue)

  data = [
      {
          'city': city,
          'state': state,
          'venues': venues
      }
      for (city, state), venues in grouped_venues.items()
  ]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search = request.form.get('search_term');

  results = Venue.query.filter(Venue.name.match(f'%{search}%')).all()
  venues = [{
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len(venue.upcoming_shows)
          } for venue in results]
  response = {'count': len(results), 'data': list(venues)}
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  if venue_id is None:
     return abort(404)
  # shows the venue page with the given venue_id
  venue = Venue.query.filter_by(id=venue_id).first_or_404()

  if venue is None:
    abort(404)

  data = venue.getDataById()
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
      form = VenueForm(request.form)

      if form.validate_on_submit:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        address = request.form.get('address')
        phone = request.form.get('phone')
        genres = request.form.getlist('genres')  # If multiple genres are selected
        genres = ', '.join(genres)
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
                      website=website_link,
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
      'genres': venue.genres.split(', '),
      'address': venue.address,
      'city': venue.city,
      'state': venue.state,
      'phone': venue.phone,
      'website': venue.website,
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
    form.genres.data = ', '.join(form.genres.data)
    venue.name = form.name.data
    venue.genres = form.genres.data
    venue.address = form.address.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.website = form.website_link.data
    venue.facebook_link = form.facebook_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    venue.image_link = form.image_link.data
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
