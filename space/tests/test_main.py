import unittest

import space.main as main
import mock
import json


class SpaceTestCase(unittest.TestCase):
    """Functional tests"""
    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()
        main.init_db()

    def tearDown(self):
        main.Base.metadata.drop_all(main.engine)

    @staticmethod
    def decode_json_response(response, msg='Space'):
        """Decode json from response"""
        return json.loads(response.data.decode('utf8'))[msg]

    def populate_data(self, name, orgid):
        self.app.post("/{}/spaces/{}".format(orgid, name))

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

    @mock.patch('space.main.is_org_exists', return_value=True)
    def test_GET_all_orgs(self, org_mock):
        """GET all spaces respond with json object with all spaces of specific org"""
        self.populate_data('space1', 1)
        self.populate_data('space2', 1)
        self.populate_data('space3', 1)
        resp = self.app.get('/1/spaces')
        resp_data = self.decode_json_response(resp)
        self.assertIn(self.get_dict(1, 'space1'), resp_data)
        self.assertIn(self.get_dict(1, 'space2'), resp_data)
        self.assertIn(self.get_dict(1, 'space3'), resp_data)
        self.assertEquals(len(resp_data), 3)

    @mock.patch('space.main.is_org_exists', return_value=True)
    def test_GET_with_space_name(self, org_mock):
        """GET specific space with name always respond with single entry"""
        self.populate_data('space1', 1)
        self.populate_data('space2', 1)
        resp = self.app.get('/1/spaces/space1')
        resp_data = self.decode_json_response(resp)
        self.assertIn(self.get_dict(1, 'space1'), resp_data)
        self.assertEquals(len(resp_data), 1)

    @mock.patch('space.main.is_org_exists', return_value=True)
    def test_GET_with_space_id(self, org_mock):
        """GET specific space with id always respond with single entry"""
        self.populate_data('space1', 1)
        self.populate_data('space2', 1)
        resp = self.app.get('/spaces/1')
        resp_data = self.decode_json_response(resp)
        self.assertIn(self.get_dict(1, 'space1'), resp_data)
        self.assertEquals(len(resp_data), 1)

    @mock.patch('space.main.is_org_exists', return_value=True)
    def test_GET_non_existant_space_with_id(self, org_mock):
        """GET nonexistant space with id respond with 404"""
        resp = self.app.get('/spaces/101')
        self.assertIn(b'Resource with that ID no longer exists', resp.data)
        self.assertEquals(resp.status_code, 404)

    @mock.patch('space.main.is_org_exists', return_value=True)
    def test_GET_non_existant_space_with_name(self, org_mock):
        """GET nonexistant space by name respond with 404"""
        self.populate_data('space1', 1)
        resp = self.app.get('/1/spaces/non_existant')
        self.assertIn(b'Resource with that ID no longer exists', resp.data)
        self.assertEquals(resp.status_code, 404)

    @mock.patch('space.main.is_org_exists', return_value=True)
    def test_POST_space(self, org_mock):
        """POST to space with name"""
        resp = self.app.post('/1/spaces/foo')
        self.assertIn(self.get_dict(1, 'foo'),
                      self.decode_json_response(resp))

    @mock.patch('space.main.is_org_exists', return_value=False)
    def test_POST_space_with_nonexistant_org(self, org_mock):
        """POST to org with nonexistant org fail with 403"""
        resp = self.app.post('/101/spaces/foo')
        self.assertIn(b"Something's not right!! You may not have access to provided org", resp.data)
        self.assertEquals(resp.status_code, 403)

    def test_POST_space_without_name_fail(self):
        """POST without name fail with 405"""
        resp = self.app.post('/1/spaces/')
        self.assertEquals(self.decode_json_response(resp, 'message'),
                          'The method is not allowed for the requested URL.')
        self.assertEquals(resp.status_code, 405)

    def test_POST_space_with_id_fail(self):
        """POST with id fail with 405"""
        resp = self.app.post('/spaces/1')
        self.assertEquals(self.decode_json_response(resp, 'message'),
                          'The method is not allowed for the requested URL.')
        self.assertEquals(resp.status_code, 405)

    def test_PUT_space_fail(self):
        """PUT fail with 405 as it is not implemented"""
        resp = self.app.put('/1/spaces/')
        self.assertEquals(self.decode_json_response(resp, 'message'),
                          'The method is not allowed for the requested URL.')
        self.assertEquals(resp.status_code, 405)

    @mock.patch('space.main.is_org_exists', return_value=True)
    def test_DELETE_all_spaces_of_an_org(self, org_mock):
        """DELETE all spaces of a org"""
        self.populate_data('space1', 1)
        self.populate_data('space2', 1)
        self.populate_data('space3', 1)
        self.app.delete('/1/spaces/')
        resp = self.app.get('/1/spaces')
        resp_data = self.decode_json_response(resp)
        self.assertEquals(len(resp_data), 0)

    @mock.patch('space.main.is_org_exists', return_value=True)
    def test_DELETE_a_space_of_an_org(self, org_mock):
        """DELETE specific org of a org"""
        self.populate_data('space1', 1)
        self.populate_data('space2', 1)
        self.app.delete('/1/spaces/space1')
        resp = self.app.get('/1/spaces')
        resp_data = self.decode_json_response(resp)
        self.assertEquals(len(resp_data), 1)
        self.assertNotIn(self.get_dict(1, 'space1'), resp_data)
        self.assertIn(self.get_dict(1, 'space2'), resp_data)

    @mock.patch('space.main.is_org_exists', return_value=True)
    def test_DELETE_space_with_id(self, org_mock):
        """DELETE space with id"""
        self.populate_data('space1', 10)
        self.populate_data('space2', 10)
        self.app.delete('/spaces/1')
        resp = self.app.get('/10/spaces')
        resp_data = self.decode_json_response(resp)
        self.assertEquals(len(resp_data), 1)
        self.assertNotIn(self.get_dict(10, 'space1'), resp_data)
        self.assertIn(self.get_dict(10, 'space2'), resp_data)
