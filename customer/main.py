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

    CUST_STATUS = {
        0: {'id': 'free_tier', 'desc': 'Free Tier'},
        1: {'id': 'active', 'desc': 'Active'},
        -1: {'id': 'inactive', 'desc': 'Inactive'},
        -2: {'id': 'disabled', 'desc': 'Disabled'}
    }
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    custid = Column(String(20), unique=True, nullable=False)
    email = Column(String(100), nullable=False)
    # status: status of customer
    # 0 - free tier, 1 - active, -1 - inactive, -2 - disabled
    status = Column(Integer, default=0)

    def __init__(self, name=None, email=None, custid=None, status=None):
        self.name = name
        self.email = email
        self.custid = custid
        self.status = status

    def __repr__(self):
        return '<Customers %r>' % self.name

    def _is_custid_exists(self, custid):
        return True if self.query.filter_by(custid=custid).count() > 0 else False

    def add(self):
        num_letters = 3
        upper_name = self.name.upper()
        self.custid = upper_name[:num_letters]
        while self._is_custid_exists(self.custid):
            num_letters += 1
            self.custid = upper_name[:num_letters]
        try:
            db_session.add(self)
            db_session.commit()
        except exc.IntegrityError as err:
            abort(409, "Duplicate details - %s" % (err))
        return True

    def show(self, name=None, custid=None, status=None):
        fields = ['name', 'custid', 'status']
        # TODO: we would have to implement using combinatoin of params
        if custid:
            return self._object_as_dict(self.query.filter_by(custid=custid).with_entities(
                self.custid, self.name, self.email, self.status
            ))
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
            abort(400, "Delete customer failed - %s" % err)

    def _fix_output(self, data):
        out = {}
        for column in inspect(data).mapper.column_attrs:
            if column.key == 'id':
                continue
            if column.key == 'status':
                out.update({'status': self.CUST_STATUS[getattr(data, column.key)]['desc']})
            else:
                out.update({column.key: getattr(data, column.key)})

        return out

    def _object_as_dict(self, obj):
        return list(map(self._fix_output, obj))


class CustomerManager(Resource):
    parser = reqparse.RequestParser()
    #parser.add_argument("apps", choices=("wordpress",), required=True, help="Unknown App - {error_msg}")
    parser.add_argument("email", required=True, help="Email id is required")

    def get(self, name=None, custid=None):
        cust = Customers().show(name=name, custid=custid)
        if cust or not custid or not name:
            return jsonify(Customer=cust)
        else:
            abort(410, "Resource with that ID no longer exists")

    def post(self, name):
        args = self.parser.parse_args()
        Customers(name, args["email"]).add()
        return self.get(name)

    def delete(self, name):
        Customers().delete(name)
        return jsonify({'status': True})


api.add_resource(CustomerManager, "/customers", "/customers/",
                 "/customers/<string:name>")


def init_db():
    Base.metadata.create_all(bind=engine)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == "__main__":
    init_db()
    app.run(debug=True,
            host=os.getenv("CUSTOMER_APP_LISTEN_ADDR", "127.0.0.1"),
            port=int(os.getenv("CUSTOMER_APP_LISTEN_PORT", "5000")))
