from . import db

class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"), nullable=False)  # Foreign key referencing Venue.id

    def __init__(self, venue_id, artist_id, start_time):
        self.venue_id = venue_id
        self.artist_id = artist_id
        self.start_time = start_time
    def getDataById(self):
        return {
            'venue_id': self.venue.id,
            'venue_name': self.venue.name,
            'artist_id': self.artist.id,
            'artist_name': self.artist.name,
            'artist_image_link': self.artist.image_link,
            'start_time': self.start_time.isoformat()
        }

    def __repr__(self):
        return (
            f"<Show(id={self.id}, "
            f"start_time='{self.start_time}', "
            f"artist_id={self.artist_id}, "
            f"venue_id={self.venue_id})>"
        )
