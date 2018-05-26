from flask import Flask, jsonify, abort
from flask_restful import Resource, Api, reqparse
from sqlalchemy import inspect
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, and_, UniqueConstraint
from sqlalchemy import exc

import requests

import os

app = Flask(__name__)

DATABASE_URI = "sqlite:////tmp/mpaas_org.db"

customer_service_url = os.getenv('CUSTOMER_SERVICE_URL', 'http://localhost:5000/customers')

app.config["DATABASE_URI"] = os.getenv("MPAAS_ORG_DB_URL", DATABASE_URI)
engine = create_engine(app.config["DATABASE_URI"], convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

api = Api(app)


def is_customer_exists(custid):
    resp = requests.get("{}/{}".format(customer_service_url, custid))
    if resp.status_code == 200:
        return True


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
    custid = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    # status: status of customer
    # 0 - free tier, 1 - active, -1 - inactive, -2 - disabled
    status = Column(Integer, default=0)
    __table_args__ = (UniqueConstraint('custid', 'name', name='_custid_name_uc'),)

    def __init__(self, custid=None, name=None, orgid=None, status=None):
        self.name = name
        self.orgid = orgid
        self.custid = custid
        self.status = status

    def __repr__(self):
        return '<Orgs %r>' % self.name

    def add(self):
        try:
            db_session.add(self)
            db_session.commit()
        except exc.IntegrityError as err:
            print(err)
            abort(409, "Duplicate details")
        return True

    def show(self):
        fields = ['name', 'custid', 'status']
        # TODO: we would have to implement using combinatoin of params
        if self.name:
            return self._object_as_dict(self.query.filter(and_(Orgs.name == self.name, Orgs.custid == self.custid)).all())
        elif self.orgid:
            return self._object_as_dict(self.query.filter(Orgs.id == self.orgid).all())
        elif self.status:
            return self._object_as_dict(self.query.filter(and_(Orgs.name == self.status, Orgs.custid == self.custid)).all())
        else:
            return self._object_as_dict(self.query.filter(Orgs.custid == self.custid).all())

    def delete(self):
        try:
            if self.name:
                cols_deleted = self.query.filter(and_(Orgs.custid == self.custid, Orgs.name == self.name)).delete()
            elif self.status:
                cols_deleted = self.query.filter(and_(Orgs.custid == self.custid, Orgs.status == self.status)).delete()
            else:
                cols_deleted = self.query.filter(Orgs.custid == self.custid).delete()

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


class OrgBase(Resource):
    def get(self, custid=None, name=None, orgid=None):
        if custid:
            if not is_customer_exists(custid):
                print("Customer id {} does not exist".format(custid))
                abort(403, "Something's not right!! You may not have access to the customer")
        else:
            if name:
                abort(400, "Customer id not known")
        org = Orgs(custid, name=name, orgid=orgid).show()

        if org or (not name and not orgid):
            return jsonify(Org=org)
        else:
            abort(410, "Resource with that ID no longer exists")


class OrgManager(OrgBase):
    parser = reqparse.RequestParser()
    #parser.add_argument("apps", choices=("wordpress",), required=True, help="Unknown App - {error_msg}")
    parser.add_argument("status", help="Status of the org")

    def post(self, custid, name=None):
        if not name:
            abort(400, "Org name is required")
        if not is_customer_exists(custid):
            print("Customer id {} does not exist".format(custid))
            abort(403, "Something's not right!! You may not have access to the customer")
        args = self.parser.parse_args()
        Orgs(custid, name, args["status"]).add()
        return self.get(custid, name)

    def delete(self, custid, name=None):
        if not is_customer_exists(custid):
            print("Customer id {} does not exist".format(custid))
            abort(403, "Something's not right!! You may not have access to the customer")
        if name:
            Orgs(custid, name).delete()
        else:
            Orgs(custid).delete()
        return jsonify({'status': True})

# All get, post and delete allowed
api.add_resource(OrgManager, "/<int:custid>/orgs", "/<int:custid>/orgs/",
                 "/<int:custid>/orgs/<string:name>")

# Only get is allowed
api.add_resource(OrgBase, "/orgs/<int:orgid>")


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
