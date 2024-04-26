from . import db

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"), nullable=False)  # Foreign key referencing Venue.id

    def __repr__(self):
        return (
            f"<Show(id={self.id}, "
            f"start_time='{self.start_time}', "
            f"artist_id={self.artist_id}, "
            f"venue_id={self.venue_id})>"
        )
