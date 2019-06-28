import uuid
import re
import json
from collections import OrderedDict
from collections import defaultdict
from datetime import datetime

from flask_restplus import Resource
from flask import request
from sqlalchemy import func


from database.models import Movies, Schedules
from api.restplus import api
from database import db


ns = api.namespace('/', description="movies api")

"""
Generate uuid. To ensure collisions never happen check if uuid already exists in the db
"""


def generate_uuid(table_name):
    s = uuid.uuid4()
    if table_name == 'movie':
        qry = Movies.query.filter(Movies.uuid == str(s)).all()
    else:
        qry = Schedules.query.filter(Schedules.uuid == str(s)).all()

    if len(qry) > 0:
        generate_uuid(table_name)
    else:
        return str(s)


@ns.route('/fetch/now_showing/', methods=['POST'])
class FetchNowShowing(Resource):
    def post(self):
        response = {}
        try:
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
                    uuid=generate_uuid('movie')
                )

                db.session.add(new_record)
                db.session.commit()

            response.update({'status': 'success', 'msg': 'JSON file parsed successfully'})
        except FileNotFoundError:
            response.update({'status': "failed",
                             'msg': "The file was not found! Please check if it's in the correct directory"})
        except Exception as e:
            response.update({'status': "failed", 'msg': str(e)})
        finally:
            return response


@ns.route('/fetch/coming_soon/', methods=['POST'])
class FetchComingSoon(Resource):
    def post(self):
        response = {}
        try:
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
                    uuid=generate_uuid('movie')
                )

                db.session.add(new_record)
                db.session.commit()
            response.update({'status': 'success', 'msg': 'JSON file parsed successfully'})
        except FileNotFoundError:
            response.update({'status': "failed",
                             'msg': "The file was not found! Please check if it's in the correct directory"})
        except Exception as e:
            response.update({'status': "failed", 'msg': str(e)})
        finally:
            return response


@ns.route('/fetch/schedules/', methods=['POST'])
class FetchSchedules(Resource):
    def post(self):
        response = {}
        try:
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
                    show_date=data['result'][i]['screening'].split(' ')[:1],
                    seat_type=data['result'][i]['seat_type'],
                    theater_code=data['result'][i]['theater_code'],
                    uuid=generate_uuid('schedule')
                )

                db.session.add(new_record)
                db.session.commit()

            response.update({'status': 'success', 'msg': 'JSON file parsed successfully'})
        except FileNotFoundError:
            response.update({'status': "failed",
                             'msg': "The file was not found! Please check if it's in the correct directory"})
        except Exception as e:
            response.update({'status': "failed", 'msg': str(e)})
        finally:
            return response


"""
The idea here is to check movie_title if it has a variant via regex
regex check for words inside a parenthesis and if it occurs at the start of the string
append that to a defaultlist and update list of variant of movie_title if movie_title exists in our dict
"""


@ns.route('/movies', methods=['GET'])
class GetMovies(Resource):
    def get(self):
        response = {}
        try:
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

            response.update({"results": [*out.values()]})
        except Exception as e:
            response.update({'status': "failed", 'msg': str(e)})

        finally:
            return response


@ns.route('/movies/<uuid>/schedules', methods=['GET'])
class GetMoviesSchedule(Resource):
    def get(self, uuid):
        response = {}
        try:
            filter_date = request.args.get('show_date', None)

            if filter_date:
                date_str = datetime.strftime(datetime.strptime(filter_date, '%m/%d/%Y'), '%Y-%m-%d')
            else:
                date_str = None

            filter_data = {'show_date': date_str}
            filter_data = {key: value for (key, value) in filter_data.items() if value}

            all_movie_schedules = db.session.query(Schedules.uuid.label("id"), Schedules.cinema_code,
                                                   Movies.uuid.label("movie"), Schedules.price, Schedules.seat_type,
                                                   func.strftime('%m/%d/%Y', Schedules.show_date), func.group_concat(
                                                   func.strftime('%H:%M', Schedules.screening)).label("start_times"),
                                                   Schedules.theater_code, Schedules.variant)\
                                            .filter(Schedules.movie_id == Movies.id)\
                                            .filter(Movies.uuid == uuid)\
                                            .filter_by(**filter_data)\
                                            .group_by(Schedules.movie_title, Schedules.cinema_code,
                                                      Schedules.price, Schedules.theater_code,
                                                      Schedules.variant, Schedules.movie_id,
                                                      func.strftime('%m/%d/%Y', Schedules.show_date))\
                                            .all()

            all_movie_sched_list = []

            for row in all_movie_schedules:
                rows_as_dicts = {
                    'id': row[0],
                    'schedule': {
                        'cinema_code': row[1],
                        'movie': row[2],
                        'price': str(int(float(row[3]))),
                        'seat_type': row[4],
                        'show_date': datetime.strftime(datetime.strptime(row[5], "%m/%d/%Y"), '%d %b %Y'),
                        'start_times': row[6].split(','),
                        'theater_code': row[7],
                        'variant': row[8] if row[8] != '' else None
                    }
                }
                all_movie_sched_list.append(rows_as_dicts)

            response.update({'results': all_movie_sched_list})

        except Exception as e:
            response.update({'status': "failed", 'msg': str(e)})

        finally:
            return response