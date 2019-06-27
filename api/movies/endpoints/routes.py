from flask_restplus import Resource
from database.models import Movies, Schedules
from api.restplus import api
from sqlalchemy import inspect
from sqlalchemy import case, func, sql, select, and_
from database import db
import json
from collections import OrderedDict
import uuid
import re
from collections import defaultdict

ns = api.namespace('/', description="movies api")


@ns.route('/fetch/now_showing/', methods=['POST'])
class FetchNowShowing(Resource):
    def post(self):
        def generate_uuid():
            s = uuid.uuid4()
            qry = Movies.query.filter(Movies.uuid == str(s)).all()

            if len(qry) > 0:
                generate_uuid()
            else:
                return str(s)

        with open('../movie_api/json_files/now_showing.json') as f:
            data = json.load(f, object_pairs_hook=OrderedDict)

        for i in range(len(data['results'])):
            new_record = Movies(
                id=data['results'][i]['id'],
                rating=data['results'][i]['rating'],
                synopsis=data['results'][i]['synopsis'],
                movie_title=data['results'][i]['movie_title'],
                image_url=data['results'][i]['image_url'],
                cast=data['results'][i]['cast'],
                release_date=None,
                uuid=generate_uuid()
            )

            db.session.add(new_record)
            db.session.commit()


@ns.route('/fetch/coming_soon/', methods=['POST'])
class FetchComingSoon(Resource):
    def post(self):
        def generate_uuid():
            s = uuid.uuid4()
            qry = Movies.query.filter(Movies.uuid == str(s)).all()

            if len(qry) > 0:
                generate_uuid()
            else:
                return str(s)

        with open('../movie_api/json_files/coming_soon.json') as f:
            data = json.load(f, object_pairs_hook=OrderedDict)

        for i in range(len(data['results'])):
            new_record = Movies(
                id=data['results'][i]['id'],
                rating=data['results'][i]['rating'],
                synopsis=data['results'][i]['synopsis'],
                movie_title=data['results'][i]['movie_title'],
                image_url=data['results'][i]['image_url'],
                cast=data['results'][i]['cast'],
                release_date=data['results'][i]['release_date'],
                uuid=generate_uuid()
            )

            db.session.add(new_record)
            db.session.commit()


@ns.route('/fetch/schedules/', methods=['POST'])
class FetchSchedules(Resource):
    def post(self):
        with open('../movie_api/json_files/schedules.json') as f:
            data = json.load(f, object_pairs_hook=OrderedDict)

        for i in range(len(data['result'])):
            new_record = Schedules(
                id=data['result'][i]['id'],
                movie_id=data['result'][i]['movie_id'],
                movie_title=data['result'][i]['movie_title'],
                cinema_code=data['result'][i]['cinema_code'],
                price=data['result'][i]['price'],
                variant=data['result'][i]['variant'],
                cinema_name=data['result'][i]['cinema_name'],
                screening=data['result'][i]['screening'],
                seat_type=data['result'][i]['seat_type'],
                theater_code=data['result'][i]['theater_code']
            )

            db.session.add(new_record)
            db.session.commit()


@ns.route('/movies', methods=['GET'])
class GetMovies(Resource):
    def get(self):

        all_movies = db.session.query(Movies).all()

        variances = defaultdict(list)
        out = {}

        for row in all_movies:
            g = re.match(r'^(?:\(([^)]+)\))?\s*(.*)', row.movie_title).groups()
            if g[0]:
                variances[g[1]].append(g[0])
            out[g[1]] = {
                "id": row.uuid,
                "movie": {
                    "advisory_rating": row.rating,
                    "canonical_title": row.movie_title,
                    "cast": row.cast.split(','),
                    "poster_portrait": row.image_url,
                    "release_date": row.release_date,
                    "synopsis": row.synopsis,
                }
            }

        for k, v in out.items():
            out[k]['variance'] = variances[k]
        return {"results": [*out.values()]}














