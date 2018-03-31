from flask import Flask, jsonify, abort
from flask_restful import Resource, Api, reqparse
from sqlalchemy import inspect
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import exc

import os

app = Flask(__name__)

DATABASE_URI = "sqlite:////tmp/mpaas_org.db"

app.config["DATABASE_URI"] = os.getenv("MPAAS_ORG_DB_URL", DATABASE_URI)
engine = create_engine(app.config["DATABASE_URI"], convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

api = Api(app)


# Models
class Orgs(Base):
    __tablename__ = "orgs"

    ORG_STATUS = {
        0: {'id': 'free_tier', 'desc': 'Free Tier'},
        1: {'id': 'active', 'desc': 'Active'},
        -1: {'id': 'inactive', 'desc': 'Inactive'},
        -2: {'id': 'disabled', 'desc': 'Disabled'}
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    custid = Column(String(20), nullable=False)
    spaces = Column(String(200), nullable=False)
    # status: status of customer
    # 0 - free tier, 1 - active, -1 - inactive, -2 - disabled
    status = Column(Integer, default=0)

    def __init__(self, name=None, custid=None, spaces=None, status=None):
        self.name = name
        self.spaces = spaces
        self.custid = custid
        self.status = status

    def __repr__(self):
        return '<Orgs %r>' % self.name

    def add(self):
        try:
            db_session.add(self)
            db_session.commit()
        except exc.IntegrityError as err:
            abort(409, "Duplicate details - %s" % (err))
        return True

    def show(self, name=None, custid=None, status=None):
        fields = ['name', 'custid', 'status', 'spaces']
        # TODO: we would have to implement using combinatoin of params
        if custid:
            return self._object_as_dict(self.query.filter_by(custid=custid).all())
        elif name:
            return self._object_as_dict(self.query.filter_by(name=name).all())
        elif status:
            return self._object_as_dict(self.query.filter_by(status=status).all())
        else:
            return self._object_as_dict(self.query.all())

    def delete(self, name):
        try:
            cols_deleted = self.query.filter_by(name=name).delete()
            if cols_deleted == 0:
                abort(404, "Requested entity does not exist")
            db_session.commit()
        except exc.SQLAlchemyError as err:
            abort(400, "Delete org failed - %s" % err)

    def _fix_output(self, data):
        out = {}
        for column in inspect(data).mapper.column_attrs:
            if column.key == 'id':
                continue
            if column.key == 'status':
                out.update({'status': self.ORG_STATUS[getattr(data, column.key)]['desc']})
            else:
                out.update({column.key: getattr(data, column.key)})

        return out

    def _object_as_dict(self, obj):
        return list(map(self._fix_output, obj))


class OrgManager(Resource):
    parser = reqparse.RequestParser()
    #parser.add_argument("apps", choices=("wordpress",), required=True, help="Unknown App - {error_msg}")
    parser.add_argument("custid", required=True, help="Customer id is required")
    parser.add_argument("spaces", help="List of Spaces within the org")
    parser.add_argument("status", help="Status of the org")

    def get(self, name=None, custid=None):
        org = Orgs().show(name=name, custid=custid)
        if org or not custid or not name:
            return jsonify(Org=org)
        else:
            abort(410, "Resource with that ID no longer exists")

    def post(self, name):
        args = self.parser.parse_args()
        Orgs(name, args["custid"], args["spaces"], args["status"]).add()
        return self.get(name)

    def delete(self, name):
        Orgs().delete(name)
        return jsonify({'status': True})


api.add_resource(OrgManager, "/orgs", "/orgs/",
                 "/orgs/<string:name>")


def init_db():
    Base.metadata.create_all(bind=engine)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == "__main__":
    init_db()
    app.run(debug=True,
            host=os.getenv("ORG_APP_LISTEN_ADDR", "127.0.0.1"),
            port=int(os.getenv("ORG_APP_LISTEN_PORT", "5001")))
