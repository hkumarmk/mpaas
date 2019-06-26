import unittest

import org.main as main
import mock
import json


class OrgTestCase(unittest.TestCase):
    """Functional tests"""
    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        main.init_db()

    def tearDown(self):
        main.Base.metadata.drop_all(main.engine)

    @staticmethod
    def decode_json_response(response, msg='Org'):
        """Decode json from response"""
        return json.loads(response.data.decode('utf8'))[msg]

    def populate_data(self, org_name, cust_id):
        self.app.post("/{}/orgs/{}".format(cust_id, org_name))

    @staticmethod
    def get_dict(id_, name, status='Free Tier'):
        return dict(
            custid=id_,
            name=name,
            status=status
        )

    @mock.patch('requests.get')
    def test_is_customer_exists(self, requests_mock):
        """is_customer_exists return True if customer exists"""
        req_instance = requests_mock()
        req_instance.status_code = 200
        self.assertEquals(main.is_customer_exists(100), True)

    @mock.patch('requests.get')
    def test_is_customer_exists_non_existant_customer(self, requests_mock):
        """is_customer_exists return None if customer does NOT exists"""
        req_instance = requests_mock()
        req_instance.status_code = 404
        self.assertEquals(main.is_customer_exists(100), None)

    @mock.patch('org.main.is_customer_exists', return_value=True)
    def test_GET_all_orgs(self, cust_mock):
        """GET all orgs respond with json object with all orgs of specific customer"""
        self.populate_data('org1', 1)
        self.populate_data('org2', 1)
        self.populate_data('org3', 1)
        resp = self.app.get('/1/orgs')
        resp_data = self.decode_json_response(resp)
        self.assertIn(self.get_dict(1, 'org1'), resp_data)
        self.assertIn(self.get_dict(1, 'org2'), resp_data)
        self.assertIn(self.get_dict(1, 'org3'), resp_data)
        self.assertEquals(len(resp_data), 3)

    @mock.patch('org.main.is_customer_exists', return_value=True)
    def test_GET_with_org_name(self, cust_mock):
        """GET specific org with name always respond with single entry"""
        self.populate_data('org1', 1)
        resp = self.app.get('/1/orgs/org1')
        resp_data = self.decode_json_response(resp)
        self.assertIn(self.get_dict(1, 'org1'), resp_data)
        self.assertEquals(len(resp_data), 1)

    @mock.patch('org.main.is_customer_exists', return_value=True)
    def test_GET_with_org_id(self, cust_mock):
        """GET specific org with id always respond with single entry"""
        self.populate_data('org1', 1)
        resp = self.app.get('/orgs/1')
        resp_data = self.decode_json_response(resp)
        self.assertIn(self.get_dict(1, 'org1'), resp_data)
        self.assertEquals(len(resp_data), 1)

    @mock.patch('org.main.is_customer_exists', return_value=True)
    def test_GET_non_existant_org_with_id(self, cust_mock):
        """GET nonexistant org with id respond with 404"""
        resp = self.app.get('/orgs/101')
        self.assertIn(b'Resource with that ID no longer exists', resp.data)
        self.assertEquals(resp.status_code, 404)

    @mock.patch('org.main.is_customer_exists', return_value=True)
    def test_GET_non_existant_org_with_name(self, cust_mock):
        """GET nonexistant org by name respond with 404"""
        self.populate_data('org1', 1)
        resp = self.app.get('/1/orgs/non_existant')
        self.assertIn(b'Resource with that ID no longer exists', resp.data)
        self.assertEquals(resp.status_code, 404)

    @mock.patch('org.main.is_customer_exists', return_value=True)
    def test_POST_org(self, cust_mock):
        """POST to org with name"""
        resp = self.app.post('/1/orgs/foo')
        self.assertIn(self.get_dict(1, 'foo'),
                      self.decode_json_response(resp))

    @mock.patch('org.main.is_customer_exists', return_value=False)
    def test_POST_org_with_nonexistant_customer(self, cust_mock):
        """POST to org with nonexistant customer fail with 403"""
        resp = self.app.post('/101/orgs/foo')
        self.assertIn(b"Something's not right!! You may not have access to provided customer", resp.data)
        self.assertEquals(resp.status_code, 403)

    def test_POST_org_without_name_fail(self):
        """POST without name fail with 405"""
        resp = self.app.post('/1/orgs/')
        self.assertEquals(self.decode_json_response(resp, 'message'),
                          'The method is not allowed for the requested URL.')
        self.assertEquals(resp.status_code, 405)

    def test_POST_org_with_id_fail(self):
        """POST with id fail with 400"""
        resp = self.app.post('/orgs/1')
        self.assertEquals(self.decode_json_response(resp, 'message'),
                          'The method is not allowed for the requested URL.')
        self.assertEquals(resp.status_code, 405)

    def test_PUT_org_fail(self):
        """PUT fail with 405 as it is not implemented"""
        resp = self.app.put('/1/orgs/')
        self.assertEquals(self.decode_json_response(resp, 'message'),
                          'The method is not allowed for the requested URL.')
        self.assertEquals(resp.status_code, 405)

    @mock.patch('org.main.is_customer_exists', return_value=True)
    def test_DELETE_all_orgs_of_a_customer(self, cust_mock):
        """DELETE all orgs of a customer"""
        self.populate_data('org1', 1)
        self.populate_data('org2', 1)
        self.populate_data('org3', 1)
        self.app.delete('/1/orgs/')
        resp = self.app.get('/1/orgs')
        resp_data = self.decode_json_response(resp)
        self.assertEquals(len(resp_data), 0)

    @mock.patch('org.main.is_customer_exists', return_value=True)
    def test_DELETE_an_org_of_a_customer(self, cust_mock):
        """DELETE specific org of a customer"""
        self.populate_data('org1', 1)
        self.populate_data('org2', 1)
        self.app.delete('/1/orgs/org1')
        resp = self.app.get('/1/orgs')
        resp_data = self.decode_json_response(resp)
        self.assertEquals(len(resp_data), 1)
        self.assertNotIn(self.get_dict(1, 'org1'), resp_data)
        self.assertIn(self.get_dict(1, 'org2'), resp_data)

    @mock.patch('org.main.is_customer_exists', return_value=True)
    def test_DELETE_org_with_id(self, cust_mock):
        """DELETE org with id"""
        self.populate_data('org1', 10)
        self.populate_data('org2', 10)
        self.app.delete('/orgs/1')
        resp = self.app.get('/10/orgs')
        resp_data = self.decode_json_response(resp)
        self.assertEquals(len(resp_data), 1)
        self.assertNotIn(self.get_dict(10, 'org1'), resp_data)
        self.assertIn(self.get_dict(10, 'org2'), resp_data)
