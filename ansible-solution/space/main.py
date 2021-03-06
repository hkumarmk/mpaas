import os

from flask import abort, Flask, jsonify
from flask_restful import Api, reqparse, Resource
import requests
from sqlalchemy import and_, Column, create_engine, inspect, Integer, String, UniqueConstraint
from sqlalchemy import exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)

DATABASE_URI = "sqlite:////tmp/mpaas_space.db"
org_service_url = os.getenv('ORG_SERVICE_URL', 'http://localhost:5000/orgs')

app.config["DATABASE_URI"] = os.getenv("MPAAS_SPACE_DB_URL", DATABASE_URI)
engine = create_engine(app.config["DATABASE_URI"], convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

api = Api(app)


def is_org_exists(orgid):
    resp = requests.get("{}/{}".format(org_service_url, orgid))
    if resp.status_code == 200:
        return True


# Models
class Spaces(Base):
    __tablename__ = "spaces"

    id = Column(Integer, primary_key=True)
    orgid = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    # status: status of customer
    __table_args__ = (UniqueConstraint('orgid', 'name', name='_orgid_name_uc'),)

    def __init__(self, orgid=None, name=None, id=None):
        self.name = name
        self.id = id
        self.orgid = orgid

    def __repr__(self):
        return '<Space %r-%r>' % (self.orgid, self.name)

    def add(self):
        try:
            db_session.add(self)
            db_session.commit()
        except exc.IntegrityError as err:
            print(err)
            abort(409, "Duplicate details")
        return True

    def show(self):
        # TODO: we would have to implement using combinatoin of params
        if self.name:
            return self._object_as_dict(self.query.filter(and_(Spaces.name == self.name, Spaces.orgid == self.orgid)).all())
        elif self.id:
            return self._object_as_dict(self.query.filter(Spaces.id == self.id).all())
        else:
            return self._object_as_dict(self.query.filter(Spaces.orgid == self.orgid).all())

    def delete(self):
        try:
            if self.name:
                cols_deleted = self.query.filter(and_(Spaces.orgid == self.orgid, Spaces.name == self.name)).delete()
            elif self.id:
                cols_deleted = self.query.filter(Spaces.id == self.id).delete()
            else:
                cols_deleted = self.query.filter(Spaces.orgid == self.orgid).delete()

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
            out.update({column.key: getattr(data, column.key)})

        return out

    def _object_as_dict(self, obj):
        return list(map(self._fix_output, obj))


class SpaceBase(Resource):
    def get(self, id=None, name=None, orgid=None):
        if orgid:
            if not is_org_exists(orgid):
                print("Org id {} does not exist".format(orgid))
                abort(403, "Something's not right!! You may not have access to the org")
        else:
            if name:
                abort(400, "org id not known")
        space = Spaces(orgid, name, id).show()

        if space or (not name and not id):
            return jsonify(Space=space)
        else:
            abort(404, "Resource with that ID no longer exists")

    def delete(self, id=None, name=None, orgid=None):
        if id:
            Spaces(id=id).delete()
        elif not is_org_exists(orgid):
            print("org id {} does not exist".format(orgid))
            abort(403, "Something's not right!! You may not have access to the customer")

        if name:
            Spaces(orgid, name).delete()
        else:
            Spaces(orgid).delete()
        return jsonify({'status': True})


class SpaceManager(SpaceBase):
    parser = reqparse.RequestParser()

    def post(self, orgid, name=None):
        if not name:
            abort(400, "Space name is required")
        if not is_org_exists(orgid):
            print("Org id {} does not exist".format(orgid))
            abort(403, "Something's not right!! You may not have access to provided org")
        Spaces(orgid, name).add()
        return self.get(orgid=orgid, name=name)


# All get, post and delete allowed
api.add_resource(SpaceManager, "/<int:orgid>/spaces/<string:name>")

# Only get is allowed
api.add_resource(SpaceBase, "/spaces/<int:id>", "/<int:orgid>/spaces", "/<int:orgid>/spaces/")


def init_db():
    Base.metadata.create_all(bind=engine)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == "__main__":
    init_db()
    app.run(debug=True,
            host=os.getenv("SPACE_APP_LISTEN_ADDR", "127.0.0.1"),
            port=int(os.getenv("SPACE_APP_LISTEN_PORT", "5002")))
