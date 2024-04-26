

from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from app import app
from models import *
from helper import *
import logging
from datetime import datetime
logger = logging.getLogger(__name__)

#  ----------------------------------------------------------------
#  Artists
#  ----------------------------------------------------------------

# get all
@app.route('/artists')
def artists():
  artists = db.session.query(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=artists)

# search
@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get("search_term", "")
    artists = search_artists_by_name(search_term)
    data = build_artist_data_with_upcoming_shows_count(artists)
    response = {'count': len(artists), 'data': data}
    return render_template('pages/search_artists.html', results=response, search_term=search_term)

def search_artists_by_name(search_term):
    return Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

def build_artist_data_with_upcoming_shows_count(artists):
    def get_upcoming_shows_count(artist):
        return Show.query.filter_by(venue_id=artist.id).filter(Show.start_time > datetime.now()).count()

    return [{
        'id': artist.id,
        'name': artist.name,
        'num_upcoming_shows': get_upcoming_shows_count(artist)
    } for artist in artists]

# get by id
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = get_artist_or_abort(artist_id)
    past_shows, upcoming_shows = get_past_and_upcoming_shows(artist_id)
    data = build_artist_data(artist, past_shows, upcoming_shows)
    return render_template('pages/show_artist.html', artist=data)

def get_artist_or_abort(artist_id):
    artist = Artist.query.get(artist_id)
    if artist is None:
        abort(404)
    return artist

def get_past_and_upcoming_shows(artist_id):
    _now = datetime.now()
    past_shows = Show.query.join(Artist).filter(
        Show.venue_id == artist_id,
        Show.start_time < _now
    ).all()
    upcoming_shows = Show.query.join(Artist).filter(
        Show.venue_id == artist_id,
        Show.start_time >= _now
    ).all()
    return past_shows, upcoming_shows
def build_artist_data(artist, past_shows, upcoming_shows):

    def format_show(show):
        return {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.isoformat()
        }
    
    return {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": [format_show(show) for show in past_shows],
        "upcoming_shows": [format_show(show) for show in upcoming_shows],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)

  if artist is None:
    abort(404)
  
  data = {
      'id': artist.id,
      'name': artist.name,
      'genres': artist.genres,
      'city': artist.city,
      'state': artist.state,
      'phone': artist.phone,
      'website_link': artist.website_link,
      'facebook_link': artist.facebook_link,
      'seeking_venue': artist.seeking_venue,
      'seeking_description': artist.seeking_description,
      'image_link': artist.image_link,
  }

  form = ArtistForm(formdata=None, data=data)

  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = db.session.query(Artist).get(artist_id)

  if artist is None:
    abort(404)

  form = ArtistForm(request.form)

  if form.validate_on_submit:
      artist.name = form.name.data
      artist.genres = request.form.getlist('genres')
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.website_link = form.website_link.data
      artist.facebook_link = form.facebook_link.data
      artist.seeking_venue = form.seeking_venue.data
      artist.artist_eartistditedseeking_description = form.seeking_description.data
      artist.image_link = form.image_link.data
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return redirect(url_for('show_artist', artist_id=artist_id))
  return render_template('forms/edit_artist.html', form=form, artist=artist)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  form = ArtistForm(request.form)

  try: 
    name = form.name.data
    is_existed = db.session.query(Artist.id).filter_by(name=name).scalar() is not None

    if is_existed:
      flash(f'Artist {name} is already existed!!', 'danger')
      return render_template('forms/new_artist.html', form=form)

    if form.validate_on_submit:
      new_artist = Artist(
          name = form.name.data,
          city = form.city.data,
          state = form.state.data,
          phone = form.phone.data,
          genres = form.genres.data,
          facebook_link = form.facebook_link.data,
          image_link = form.image_link.data,
          website_link = form.website_link.data,
          seeking_venue = form.seeking_venue.data,
          seeking_description= form.seeking_description.data,
      )
      db.session.add(new_artist)
      db.session.commit()
      flash(f'Artist {name} was successfully listed!', 'success')
      return redirect(url_for('show_artist', artist_id=new_artist.id))
    return render_template('pages/home.html')
  except Exception as e:
    logger.exception(e, exc_info=True)