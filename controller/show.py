
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from app import app
from helper import ShowForm
from models import *
from sqlalchemy import and_
from datetime import datetime

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = (db.session.query(Show).join(Artist).join(Venue).all())
  shows = Show.query.order_by(Show.start_time.desc()).all()
  data = [
    {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.isoformat()
    }
    for show in shows
  ]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)

  if form.validate_on_submit:
      artist_id = form.artist_id.data
      venue_id = form.venue_id.data
      start_time = form.start_time.data
      venue_exists = Venue.query.filter_by(id=venue_id).first()

      if (venue_exists is None):
         flash(f'The venue with ID {venue_id} doesn\'t exists!', 'danger')
         return render_template('forms/new_show.html', form=form)
      
      artist_exist = Artist.query.filter_by(id=artist_id).first()

      if (artist_exist is None):
         flash(f'The artist with ID {artist_id} doesn\'t exists!', 'danger')
         return render_template('forms/new_show.html', form=form)
      
      show_exist = Show.query.filter(and_(
        Show.artist_id == artist_id,
        Show.venue_id == venue_id,
        Show.start_time == start_time)).first() is not None
      
      if(show_exist):
         flash(f'This show is already registered!', 'danger')
         return render_template('forms/new_show.html', form=form)
      
      show = Show(venue_id=venue_id, artist_id=artist_id, start_time=start_time)

      db.session.add(show)

      db.session.commit()

      flash(f'Show at {show.venue.name} with {show.artist.name} at {show.start_time} was successfully created!', 'success')

      return redirect(url_for('shows'))
  return render_template('forms/new_show.html', form=form)