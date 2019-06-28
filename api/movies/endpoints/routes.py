from flask_restplus import Resource
from database.models import Movies, Schedules
from api.restplus import api
from database import db
import json
from collections import OrderedDict
import uuid
import re
from collections import defaultdict
import pandas as pd

ns = api.namespace('/', description="movies api")


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


@ns.route('/fetch/coming_soon/', methods=['POST'])
class FetchComingSoon(Resource):
    def post(self):
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
                theater_code=data['result'][i]['theater_code'],
                uuid=generate_uuid('schedule')
            )

            db.session.add(new_record)
            db.session.commit()


"""
The idea here is to check movie_title if it has a variant via regex
regex check for words inside a parenthesis and if it occurs at the start of the string
append that to defaultlist and update [variants] of movie_title if it exists in our dict
"""


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


"""
 Gonna use pandas here
"""


@ns.route('/movies/<uuid>/schedules', methods=['GET'])
class GetMoviesSchedule(Resource):
    def get(self, uuid):

        all_movie_schedules = db.session.query(Schedules.uuid.label("id"), Schedules.cinema_code,
                                               Movies.uuid.label("movie"), Schedules.price,
                                               Schedules.seat_type, Schedules.screening,
                                               Schedules.theater_code, Schedules.variant)\
                                        .filter(Schedules.movie_id == Movies.id)\
                                        .filter(Movies.uuid == uuid)

        df = pd.read_sql(all_movie_schedules.statement, db.session.bind)

        df[['show_date', 'start_times', 'median']] = df.screening.str.split(' ', expand=True)
        df['start_times'] = df['start_times'] + df['median']
        df.drop('screening', axis=1, inplace=True)
        df.drop('median', axis=1, inplace=True)
        df_grp = df.groupby(['id', 'cinema_code', 'movie', 'price', 'seat_type', 'theater_code', 'variant'])
        df_grp_time_stacked = df_grp['start_times'].apply(list).reset_index()
        df_grp_time_stacked['start_times'] = df_grp_time_stacked['start_times'].apply(lambda x:x[0] if (len(x)==1) else x)
        print(df_grp_time_stacked)
        # return_to_dict = df_grp_time_stacked.to_dict(orient='records')
        #
        # return return_to_dict




        # start_times = defaultdict(list)
        # out = {}
        # for row in all_movie_schedules:
        #     date, time = row[5].split(" ")[:2]
        #     start_times[date].append(time)
        #     out[date] = {
        #         "schedule": {
        #             "cinema": row[1],
        #             "movie": row[2],
        #             "price": row[3],
        #             "seating_type": row[4],
        #             "show_date": date,
        #             "start_times": None,
        #             "theater": row[6],
        #             "variant": row[7]
        #         }
        #     }
        #
        # for k, v in out.items():
        #     out[k]['schedule']['start_times'] = start_times[k]
        #
        # return {"results": [*out.values()]}



0

















