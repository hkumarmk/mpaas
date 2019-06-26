import unittest

import wpaas.main as main
import mock
import json


class WPaaSTestCase(unittest.TestCase):
    """Functional tests"""
    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        main.init_db()

    def tearDown(self):
        main.Base.metadata.drop_all(main.engine)

    @staticmethod
    def decode_json_response(response, msg='WPaaS'):
        """Decode json from response"""
        return json.loads(response.data.decode('utf8'))[msg]

    def populate_data(self, name, orgid):
        self.app.post("/{}/wordpress/{}".format(orgid, name))

    @staticmethod
    def get_dict(id_, name):
        return dict(
            orgid=id_,
            name=name
        )

    @mock.patch('requests.get')
    def test_is_org_exists(self, requests_mock):
        """is_org_exists return True if org exists"""
        req_instance = requests_mock()
        req_instance.status_code = 200
        self.assertEquals(main.is_org_exists(100), True)

    @mock.patch('requests.get')
    def test_is_org_exists_non_existant_org(self, requests_mock):
        """is_org_exists return None if org does NOT exists"""
        req_instance = requests_mock()
        req_instance.status_code = 404
        self.assertEquals(main.is_org_exists(100), None)

    @mock.patch('wpaas.main.is_org_exists', return_value=True)
    def test_GET_all_wpaas(self, org_mock):
        """GET all wpaas respond with json object with all wpaas of specific org"""
        self.populate_data('wp1', 1)
        self.populate_data('wp2', 1)
        self.populate_data('wp3', 1)
        resp = self.app.get('/1/wpaas')
        resp_data = self.decode_json_response(resp)
        self.assertIn(self.get_dict(1, 'wp1'), resp_data)
        self.assertIn(self.get_dict(1, 'wp2'), resp_data)
        self.assertIn(self.get_dict(1, 'wp3'), resp_data)
        self.assertEquals(len(resp_data), 3)

    @mock.patch('wpaas.main.is_org_exists', return_value=True)
    def test_GET_with_wpaas_name(self, org_mock):
        """GET specific wpaas with name always respond with single entry"""
        self.populate_data('wp1', 1)
        self.populate_data('wp2', 1)
        resp = self.app.get('/1/wordpress/wp1')
        resp_data = self.decode_json_response(resp)
        self.assertIn(self.get_dict(1, 'wp1'), resp_data)
        self.assertEquals(len(resp_data), 1)

    @mock.patch('wpaas.main.is_org_exists', return_value=True)
    def test_GET_with_wpaas_id(self, org_mock):
        """GET specific wpaas with id always respond with single entry"""
        self.populate_data('wp1', 1)
        self.populate_data('wp2', 1)
        resp = self.app.get('/wordpress/1')
        resp_data = self.decode_json_response(resp)
        self.assertIn(self.get_dict(1, 'wp1'), resp_data)
        self.assertEquals(len(resp_data), 1)

    @mock.patch('wpaas.main.is_org_exists', return_value=True)
    def test_GET_non_existant_wpaas_with_id(self, org_mock):
        """GET nonexistant wpaas with id respond with 404"""
        resp = self.app.get('/wordpress/101')
        self.assertIn(b'Resource with that ID no longer exists', resp.data)
        self.assertEquals(resp.status_code, 404)

    @mock.patch('wpaas.main.is_org_exists', return_value=True)
    def test_GET_non_existant_wpaas_with_name(self, org_mock):
        """GET nonexistant wpaas by name respond with 404"""
        self.populate_data('wp1', 1)
        resp = self.app.get('/1/wordpress/non_existant')
        self.assertIn(b'Resource with that ID no longer exists', resp.data)
        self.assertEquals(resp.status_code, 404)

    @mock.patch('wpaas.main.is_org_exists', return_value=True)
    def test_POST_wpaas(self, org_mock):
        """POST to wpaas with name"""
        resp = self.app.post('/1/wordpress/foo')
        self.assertIn(self.get_dict(1, 'foo'),
                      self.decode_json_response(resp))

    @mock.patch('wpaas.main.is_org_exists', return_value=False)
    def test_POST_wpaas_with_nonexistant_org(self, org_mock):
        """POST to wpaas with nonexistant org fail with 403"""
        resp = self.app.post('/101/wordpress/foo')
        self.assertIn(b"Something's not right!! You may not have access to provided org", resp.data)
        self.assertEquals(resp.status_code, 403)

    def test_POST_wpaas_without_name_fail(self):
        """POST without name fail with 405"""
        resp = self.app.post('/1/wordpress/')
        self.assertEquals(self.decode_json_response(resp, 'message'),
                          'The method is not allowed for the requested URL.')
        self.assertEquals(resp.status_code, 405)

    def test_POST_wpaas_with_id_fail(self):
        """POST with id fail with 405"""
        resp = self.app.post('/wordpress/1')
        self.assertEquals(self.decode_json_response(resp, 'message'),
                          'The method is not allowed for the requested URL.')
        self.assertEquals(resp.status_code, 405)

    def test_PUT_wpaas_fail(self):
        """PUT fail with 405 as it is not implemented"""
        resp = self.app.put('/1/wordpress/')
        self.assertEquals(self.decode_json_response(resp, 'message'),
                          'The method is not allowed for the requested URL.')
        self.assertEquals(resp.status_code, 405)

    @mock.patch('wpaas.main.is_org_exists', return_value=True)
    def test_DELETE_all_wpaas_of_an_org(self, org_mock):
        """DELETE all wpaas of a org"""
        self.populate_data('wp1', 1)
        self.populate_data('wp2', 1)
        self.populate_data('wp3', 1)
        self.app.delete('/1/wordpress/')
        resp = self.app.get('/1/wpaas')
        resp_data = self.decode_json_response(resp)
        self.assertEquals(len(resp_data), 0)

    @mock.patch('wpaas.main.is_org_exists', return_value=True)
    def test_DELETE_a_wpaas_of_an_org(self, org_mock):
        """DELETE specific wpaas of an org"""
        self.populate_data('wp1', 1)
        self.populate_data('wp2', 1)
        self.app.delete('/1/wordpress/wp1')
        resp = self.app.get('/1/wpaas')
        resp_data = self.decode_json_response(resp)
        self.assertEquals(len(resp_data), 1)
        self.assertNotIn(self.get_dict(1, 'wp1'), resp_data)
        self.assertIn(self.get_dict(1, 'wp2'), resp_data)

    @mock.patch('wpaas.main.is_org_exists', return_value=True)
    def test_DELETE_wpaas_with_id(self, org_mock):
        """DELETE wpaas with id"""
        self.populate_data('wp1', 10)
        self.populate_data('wp2', 10)
        self.app.delete('/wordpress/1')
        resp = self.app.get('/10/wpaas')
        resp_data = self.decode_json_response(resp)
        self.assertEquals(len(resp_data), 1)
        self.assertNotIn(self.get_dict(10, 'wp1'), resp_data)
        self.assertIn(self.get_dict(10, 'wp2'), resp_data)
