import unittest

import customer.main as main

import json



class CustomerTestCase(unittest.TestCase):
    """Functional tests"""
    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        main.init_db()

    def tearDown(self):
        main.Base.metadata.drop_all(main.engine)

    @staticmethod
    def decode_json_response(response, msg='Customer'):
        """Decode json from response"""
        return json.loads(response.data.decode('utf8'))[msg]

    def populate_data(self):
        self.app.post("customers/www?email=www@test.com")
        self.app.post("customers/www1?email=www1@test.com")
        self.app.post("customers/www2?email=www2@test.com")
        self.app.post("customers/www3?email=www3@test.com")
        self.app.post("customers/www4?email=www4@test.com")

    @staticmethod
    def get_dict(id_, name, email, status='Free Tier'):
        return dict(
            id=id_,
            name=name,
            email=email,
            status=status
        )

    def test_GET_all_customers(self):
        """GET all customers respond with json object with all customers"""
        self.populate_data()
        resp = self.app.get('/customers')
        resp_data = self.decode_json_response(resp)
        self.assertIn(self.get_dict(1, 'www', 'www@test.com'), resp_data)
        self.assertIn(self.get_dict(2, 'www1', 'www1@test.com'), resp_data)
        self.assertIn(self.get_dict(3, 'www2', 'www2@test.com'), resp_data)
        self.assertIn(self.get_dict(4, 'www3', 'www3@test.com'), resp_data)
        self.assertIn(self.get_dict(5, 'www4', 'www4@test.com'), resp_data)
        self.assertEquals(len(resp_data), 5)

    def test_GET_with_customer_name(self):
        """GET specific customer with name always respond with single entry"""
        self.populate_data()
        resp = self.app.get('/customers/www')
        resp_data = self.decode_json_response(resp)
        self.assertIn(self.get_dict(1, 'www', 'www@test.com'), resp_data)
        self.assertEquals(len(resp_data), 1)

    def test_GET_with_customer_id(self):
        """GET specific customer with id always respond with single entry"""
        self.populate_data()
        resp = self.app.get('/customers/2')
        resp_data = self.decode_json_response(resp)
        self.assertIn(self.get_dict(2, 'www1', 'www1@test.com'), resp_data)
        self.assertEquals(len(resp_data), 1)

    def test_GET_non_existant_customer_with_name(self):
        """GET with nonexistant customer respond with 410"""
        resp = self.app.get('/customers/non_existant')
        self.assertIn(b'Resource with that ID no longer exists', resp.data)
        self.assertEquals(resp.status_code, 410)

    def test_GET_non_existant_customer_with_id(self):
        """GET with nonexistant customer with id respond with 410"""
        resp = self.app.get('/customers/100')
        self.assertIn(b'Resource with that ID no longer exists', resp.data)
        self.assertEquals(resp.status_code, 410)

    def test_POST_customer(self):
        """POST to customer with name and email"""
        resp = self.app.post('/customers/foo?email=foo@bar.com')
        self.assertIn(self.get_dict(1, 'foo', 'foo@bar.com'),
                      self.decode_json_response(resp))

    def test_POST_customer_without_email_fail(self):
        """POST without email fail with 400"""
        resp = self.app.post('/customers/foo')
        self.assertEquals(self.decode_json_response(resp, 'message'),
                          {"email": "Email id is required"})
        self.assertEquals(resp.status_code, 400)

    def test_POST_customer_without_name_fail(self):
        """POST without name fail with 405"""
        resp = self.app.post('/customers/')
        self.assertEquals(self.decode_json_response(resp, 'message'),
                          'The method is not allowed for the requested URL.')
        self.assertEquals(resp.status_code, 405)

    def test_POST_customer_with_id_fail(self):
        """POST with id fail with 400"""
        resp = self.app.post('/customers/1')
        self.assertEquals(self.decode_json_response(resp, 'message'),
                          'Name should be a string')
        self.assertEquals(resp.status_code, 400)

    def test_PUT_customer_fail(self):
        """PUT fail with 405 as it is not implemented"""
        resp = self.app.put('/customers/')
        self.assertEquals(self.decode_json_response(resp, 'message'),
                          'The method is not allowed for the requested URL.')
        self.assertEquals(resp.status_code, 405)

    def test_DELETE_customer_without_name_fail(self):
        """DELETE without name fail with 405"""
        resp = self.app.delete('/customers/')
        self.assertEquals(self.decode_json_response(resp, 'message'),
                          'The method is not allowed for the requested URL.')
        self.assertEquals(resp.status_code, 405)

    def test_DELETE_customer_with_id_fail(self):
        """DELETE with id fail with 405"""
        resp = self.app.delete('/customers/1')
        self.assertEquals(self.decode_json_response(resp, 'message'),
                          'The method is not allowed for the requested URL.')
        self.assertEquals(resp.status_code, 405)

    def test_DELETE_customer(self):
        """DELETE customer"""
        self.populate_data()
        self.app.delete('/customers/www')
        # get all customers
        resp = self.app.get('/customers/www')
        resp_data = self.decode_json_response(resp, 'message')
        self.assertEquals(resp.status_code, 410)
        self.assertEquals(resp_data, 'Resource with that ID no longer exists')
