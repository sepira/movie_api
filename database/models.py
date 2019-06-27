from datetime import datetime

from database import db


class Movies(db.Model):
    id = db.Column(db.Integer)
    rating = db.Column(db.Text)
    synopsis = db.Column(db.Text)
    movie_title = db.Column(db.Text)
    image_url = db.Column(db.Text)
    cast = db.Column(db.Text)
    release_date = db.Column(db.Text)
    uuid = db.Column(db.Text, primary_key=True)

    def __init__(self, id, rating, cast, synopsis, movie_title, image_url, uuid, release_date=None):
        self.id = id
        self.rating = rating
        self.cast = ",".join(cast)
        self.synopsis = synopsis
        self.movie_title = movie_title
        self.image_url = image_url
        self.uuid = uuid
        self.release_date = release_date


class Schedules(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer)
    movie_title = db.Column(db.Text)
    cinema_code = db.Column(db.Text)
    price = db.Column(db.Text)
    variant = db.Column(db.Text)
    cinema_name = db.Column(db.Text)
    screening = db.Column(db.Text)
    seat_type = db.Column(db.Text)
    theater_code = db.Column(db.Text)

    def __init__(self, id, movie_id, movie_title, cinema_code, price, variant, cinema_name,
                 screening, seat_type, theater_code):
        self.id = id
        self.movie_id = movie_id
        self.movie_title = movie_title
        self.cinema_code = cinema_code
        self.price = price
        self.variant = variant
        self.cinema_name = cinema_name
        self.screening = screening
        self.seat_type = seat_type
        self.theater_code = theater_code

