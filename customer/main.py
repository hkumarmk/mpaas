from flask import Flask, jsonify, abort
from flask_restful import Resource, Api, reqparse
from sqlalchemy import inspect
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import exc as sql_exc
import os

app = Flask(__name__)

DATABASE_URI = "sqlite:////tmp/mpaas_customer.db"

app.config["DATABASE_URI"] = os.getenv("MPAAS_CUSTOMER_DB_URL", DATABASE_URI)
engine = create_engine(app.config["DATABASE_URI"], convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

api = Api(app)

# Exceptions
class CustomerException(BaseException):
    pass


class CustomerAddException(CustomerException):
    pass


class CustomerDeleteException(CustomerException):
    pass


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
    email = Column(String(100), nullable=False)
    # status: status of customer
    # 0 - free tier, 1 - active, -1 - inactive, -2 - disabled
    status = Column(Integer, default=0)

    def __init__(self, name=None, email=None, status=None):
        self.name = name
        self.email = email
        self.status = status

    def __repr__(self):
        return '<Customers %r>' % self.name

    def _is_customer_exists(self, customer):
        return True if self.query.filter_by(name=customer).count() > 0 else False

    def add(self):
        num_letters = 3
        upper_name = "".join(list(filter(str.isalnum, self.name.upper())))

        try:
            db_session.add(self)
            db_session.commit()
        except sql_exc.IntegrityError:
            abort(409, "Duplicate details - The details you provided already exists")
        return self.get_cust_id(self.name)

    def show(self, name=None, cust_id=None, status=None):
        fields = ['name', 'status']
        # TODO: we would have to implement using combinatoin of params
        if name:
            return self._object_as_dict(self.query.filter_by(name=name).all())
        elif cust_id:
            return self._object_as_dict(self.query.filter_by(id=cust_id).all())
        elif status:
            return self._object_as_dict(self.query.filter_by(status=status).all())
        else:
            return self._object_as_dict(self.query.all())

    def get_cust_id(self, name):
        res = self.show(name)
        if res:
            return self.show(name)[0].get('id')
        else:
            return None

    def delete(self):
        try:
            cols_deleted = self.query.filter_by(name=self.name).delete()
            if cols_deleted == 0:
                abort(404, "Requested entity does not exist")
            db_session.commit()
        except sql_exc.SQLAlchemyError as err:
            abort(400, "Delete customer failed - %s" % err)

    def _fix_output(self, data):
        out = {}
        for column in inspect(data).mapper.column_attrs:
            if column.key == 'status':
                out.update({'status': self.CUST_STATUS[getattr(data, column.key)]['desc']})
            else:
                out.update({column.key: getattr(data, column.key)})

        return out

    def _object_as_dict(self, obj):
        return list(map(self._fix_output, obj))


class CustomerManager(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("email", required=True, help="Email id is required")

    def get(self, name=None, cust_id=None):
        cust = Customers().show(name=name, cust_id=cust_id)
        if cust or (not name and not cust_id):
            return jsonify(Customer=cust)
        else:
            abort(410, "Resource with that ID no longer exists")

    def post(self, name):
        args = self.parser.parse_args()
        cust = Customers(name, args["email"])
        if cust.get_cust_id(name):
            abort(409, "Duplicate customer name")
        # Revert customer addition with exception in case of any of the transactions failed.
        try:

            cust_id = cust.add()
        except Exception as err:
            print("Encountered error on creating customer %s" % err)
            abort(500, "Unknown error, please report")

        return self.get(name)

    def delete(self, name):
        try:
            cust_id = Customers().get_cust_id(name)
            # TODO: delete operation may be handled as seperate process, delete api operation may
            # just marked that customer as "tobe_removed" status and intimate operations to start
            # customer data removal process.
            Customers(name).delete()
        except Exception as err:
            print("Encountered error on deleting customer %s" % err)
            raise CustomerDeleteException

        return jsonify({'status': True})


api.add_resource(CustomerManager, "/customers", "/customers/",
                 "/customers/<string:name>", "/customers/<int:cust_id>")


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
