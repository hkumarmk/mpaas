from flask import Flask, request, jsonify, abort
from flask_restful import Resource, Api, reqparse
from sqlalchemy import inspect
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import exc

import os

app = Flask(__name__)

DATABASE_URI = "sqlite:////tmp/mpaas_wordpress.db"

app.config["DATABASE_URI"] = os.getenv("MPAAS_WORDPRESS_DB_URL", DATABASE_URI)
engine = create_engine(app.config["DATABASE_URI"], convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

api = Api(app)


# Models
class Wordpress(Base):
    __tablename__ = "wordpress"

    id = Column(Integer, primary_key=True)
    owner = Column(String(100), nullable=False) #should come from customer
    sitename = Column(String(100), unique=True, nullable=False)

    def __init__(self, sitename=None, owner=None):
        self.sitename = sitename
        self.owner = owner

    def __repr__(self):
        return '<wp %r>' % self.sitename

    def add(self):
        try:
            db_session.add(self)
            db_session.commit()
        except exc.IntegrityError:
            abort(409, "Duplicate site name")
        return True

    def show(self, sitename=None):
        if sitename:
            return self._object_as_dict(self.query.filter_by(sitename=sitename).all())
        else:
            return self._object_as_dict(self.query.all())

    @staticmethod
    def _object_as_dict(obj):
        dict = []
        for r in obj:
            dict.append({c.key: getattr(r, c.key).split(',')
                         if c.key == 'apps' else getattr(r, c.key)
                         for c in inspect(r).mapper.column_attrs})
        return dict


class WPInstanceManager(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("space_id", type=str, required=True, help="Space id is required")

    def get(self, sitename=None):
        wp = Wordpress().show(sitename)
        if wp or not sitename:
            return jsonify(Wordpress=wp)
        else:
            abort(410, "Resource with that ID no longer exists")

    def post(self, sitename):
        data = request.json
        args = self.parser.parse_args()
        Wordpress(sitename, args["owner"]).add()
        return self.get(sitename)

api.add_resource(WPInstanceManager, "/wp", "/wp/",
                 "/wp/<string:sitename>")


def init_db():
    Base.metadata.create_all(bind=engine)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == "__main__":
    init_db()
    app.run(debug=True,
            host=os.getenv("WP_APP_LISTEN_ADDR", "127.0.0.1"),
            port=int(os.getenv("WP_APP_LISTEN_PORT", "5010")))
