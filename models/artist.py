from . import db
from datetime import datetime

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='artist', lazy=False)
    
    def __init__(self, name, genres, city, state, phone, facebook_link):
        self.name = name
        self.genres = genres
        self.city = city
        self.state = state
        self.phone = phone
        self.facebook_link = facebook_link

    @property
    def past_shows(self):
        return [
            {
                'artist_id': show.artist.id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'start_time': show.start_time.isoformat()
            } 
            for show in self.shows 
            if show.start_time < datetime.now()
        ]
    
    @property
    def upcoming_shows(self):
        return [
            {
                'artist_id': show.artist.id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'start_time': show.start_time.isoformat()
            } 
            for show in self.shows 
            if show.start_time > datetime.now()
        ]

    def getDataById(self):
        return {
            'id': self.id,
            'name': self.name,
            'genres': self.genres.split(', '),
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link,
            'past_shows': self.past_shows,
            'upcoming_shows': self.upcoming_shows,
            'past_shows_count': len(self.past_shows),
            'upcoming_shows_count': len( self.upcoming_shows)
        }

    def __repr__(self):
        return (
            f"<Artist(id={self.id}, "
            f"name='{self.name}', "
            f"city='{self.city}', "
            f"state='{self.state}', "
            f"phone='{self.phone}', "
            f"genres='{self.genres}', "
            f"image_link='{self.image_link}', "
            f"facebook_link='{self.facebook_link}', "
            f"shows='{self.shows}')>"
        )
