

from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from app import app
from models import *
from helper import *
import logging
logger = logging.getLogger(__name__)
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.order_by(Artist.name.asc()).all()
  data = [{'id': artist.id, 'name': artist.name} for artist in artists]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search = request.form.get('search_term');

  results = Artist.query.filter(Artist.name.match(f'%{search}%')).all()
  artists = [{
            'id': artist.id,
            'name': artist.name,
            'num_upcoming_shows': len(artist.upcoming_shows)
          } for artist in results]
  response = {'count': len(results), 'data': list(artists)}
  return render_template('pages/search_artists.html', results=response, search_term=search)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  artist = Artist.query.filter_by(id=artist_id).first()
  if artist is None:
    abort(404)

  data = artist.getDataById()
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first()

  if artist is None:
    abort(404)
  
  data = {
      'id': artist.id,
      'name': artist.name,
      'genres': artist.genres.split(', '),
      'city': artist.city,
      'state': artist.state,
      'phone': artist.phone,
      'website': artist.website,
      'facebook_link': artist.facebook_link,
      'seeking_venue': artist.seeking_venue,
      'seeking_description': artist.seeking_description,
      'image_link': artist.image_link,
  }

  form = ArtistForm(formdata=None, data=data)

  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first()

  if artist is None:
    abort(404)

  form = ArtistForm(request.form)

  if form.validate_on_submit:
      form.genres.data = ', '.join(form.genres.data)
      artist.name = form.name.data
      artist.genres = form.genres.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.website = form.website_link.data
      artist.facebook_link = form.facebook_link.data
      artist.seeking_venue = form.seeking_venue.data
      artist.artist_eartistditedseeking_description = form.seeking_description.data
      artist.image_link = form.image_link.data
      db.session.commit()
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
    else:
      new_artist = Artist(
        name=form.name.data,
        genres=', '.join(form.genres.data),
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        facebook_link=form.facebook_link.data
      )
      db.session.add(new_artist)
      db.session.commit()
      flash(f'Artist {name} was successfully listed!', 'success')
      return redirect(url_for('show_artist', artist_id=new_artist.id))
  except Exception as e:
    logger.exception(e, exc_info=True)