from flask import Flask, request, jsonify, abort, make_response
from flask_restful import Resource, Api, reqparse
from sqlalchemy import inspect
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import exc
from flask_sqlalchemy import SQLAlchemy

import os

app = Flask(__name__)

DATABASE_URI = "sqlite:////tmp/mpaas_customer.db"

app.config["DATABASE_URI"] = os.getenv("MPAAS_DB_URL", DATABASE_URI)
engine = create_engine(app.config["DATABASE_URI"], convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

api = Api(app)


# Models
class Customers(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    app = Column(String(30))

    def __init__(self, name=None, app=None):
        self.name = name
        self.app = app

    def __repr__(self):
        return '<Customers %r>' % self.name

    def add(self):
        try:
            db_session.add(self)
            db_session.commit()
        except exc.IntegrityError:
            abort(409, "Duplicate customer name")
        return True

    def show(self, name=None):
        if name:
            return self.object_as_dict(self.query.filter_by(name=name).all())
        else:
            return self.object_as_dict(self.query.all())

    @staticmethod
    def object_as_dict(obj):
        dict = []
        for r in obj:
            dict.append({c.key: getattr(r, c.key)
                         for c in inspect(r).mapper.column_attrs})
        return dict


class CustomerManager(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("app", choices=("wordpress",), required=True, help="Unknown App - {error_msg}")

    def get(self, name=None):
        cust = Customers().show(name)
        if cust or not name:
            return jsonify(Customer=cust)
        else:
            abort(410, "Resource with that ID no longer exists")

    def post(self, name):
        data = request.json
        args = self.parser.parse_args()
        Customers(name, args["app"]).add()
        return self.get(name)

api.add_resource(CustomerManager, "/customers", "/customers/",
                 "/customers/<string:name>")


def init_db():
    Base.metadata.create_all(bind=engine)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
