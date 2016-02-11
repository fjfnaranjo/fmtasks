"""
fmtasks's API tests.

This module implements the tests to verify the fmtasks Flask API
"""

import json
import unittest

import fmtasks


class FmtasksTest(unittest.TestCase):
    """Test suite for imagedepot."""

    def prepare_client(self):
        fmtasks.app.config['TESTING'] = True
        fmtasks.app.config['MONGODB_DATABASE'] = "fmtasks-test"
        fmtasks.app.config['MONGODB_COLLECTION'] = "tasks-test"
        self.client = fmtasks.app.test_client()

    def setUp(self):
        self.prepare_client()
        mongo = fmtasks.get_db_collection()
        if mongo.count():
            raise Exception("Test database is not empty.")

    def tearDown(self):
        self.prepare_client()
        mongo = fmtasks.get_db_collection()
        mongo.delete_many({})

    def test_add(self):

        res = self.client.post('/task/')
        res_json = json.loads(str(res.data, 'utf8'))
        self.assertTrue(res.status_code == 400)
        self.assertTrue('errormsg' in res_json)
        self.assertTrue('content is required' in res_json['errormsg'])

        res = self.client.post(
            '/task/',
            data=json.dumps(dict(content="testvalue1")),
            content_type='application/json',
        )
        res_json = json.loads(str(res.data, 'utf8'))
        self.assertTrue(res.status_code == 201)
        self.assertTrue('id' in res_json)
        self.assertTrue('Location' in res.headers)

        testid1 = res_json["id"]

        res = self.client.post(
            '/task/'+testid1,
            data=json.dumps(dict(content="testvalue2")),
            content_type='application/json',
        )
        res_json = json.loads(str(res.data, 'utf8'))
        self.assertTrue(res.status_code == 400)
        self.assertTrue('errormsg' in res_json)
        self.assertTrue('id already exists' in res_json['errormsg'])

    def test_get(self):

        res = self.client.get('/task/')
        res_json = json.loads(str(res.data, 'utf8'))
        self.assertTrue(res.status_code == 400)
        self.assertTrue('errormsg' in res_json)
        self.assertTrue('id is required' in res_json['errormsg'])

        res = self.client.get('/task/000000000000000000000000')
        res_json = json.loads(str(res.data, 'utf8'))
        self.assertTrue(res.status_code == 404)
        self.assertTrue('errormsg' in res_json)
        self.assertTrue('task doesn\'t exists' in res_json['errormsg'])

        res = self.client.post(
            '/task/',
            data=json.dumps(dict(content="testvalue1")),
            content_type='application/json',
        )
        res_json = json.loads(str(res.data, 'utf8'))
        self.assertTrue(res.status_code == 201)
        self.assertTrue('id' in res_json)
        self.assertTrue('Location' in res.headers)

        testid1 = res_json["id"]

        res = self.client.get('/task/'+testid1)
        res_json = json.loads(str(res.data, 'utf8'))
        self.assertTrue(res.status_code == 200)
        self.assertTrue('content' in res_json)
        self.assertTrue('testvalue1' == res_json['content'])

    def test_edit(self):

        res = self.client.post(
            '/task/',
            data=json.dumps(dict(content="testvalue1")),
            content_type='application/json',
        )
        res_json = json.loads(str(res.data, 'utf8'))
        self.assertTrue(res.status_code == 201)
        self.assertTrue('id' in res_json)
        self.assertTrue('Location' in res.headers)

        testid1 = res_json["id"]

        res = self.client.put('/task/')
        res_json = json.loads(str(res.data, 'utf8'))
        self.assertTrue(res.status_code == 400)
        self.assertTrue('errormsg' in res_json)
        self.assertTrue('id is required' in res_json['errormsg'])

        res = self.client.put('/task/'+testid1)
        res_json = json.loads(str(res.data, 'utf8'))
        self.assertTrue(res.status_code == 400)
        self.assertTrue('errormsg' in res_json)
        self.assertTrue('content is required' in res_json['errormsg'])

        res = self.client.put(
            '/task/000000000000000000000000',
            data=json.dumps(dict(content="testvalue2")),
            content_type='application/json',
        )
        res_json = json.loads(str(res.data, 'utf8'))
        self.assertTrue(res.status_code == 404)
        self.assertTrue('errormsg' in res_json)
        self.assertTrue('task doesn\'t exists' in res_json['errormsg'])

        res = self.client.put(
            '/task/'+testid1,
            data=json.dumps(dict(content="testvalue3")),
            content_type='application/json',
        )
        res_json = json.loads(str(res.data, 'utf8'))
        self.assertTrue(res.status_code == 200)

        res = self.client.get('/task/'+testid1)
        res_json = json.loads(str(res.data, 'utf8'))
        self.assertTrue(res.status_code == 200)
        self.assertTrue('content' in res_json)
        self.assertTrue('testvalue3' == res_json['content'])

    def test_remove(self):

        res = self.client.post(
            '/task/',
            data=json.dumps(dict(content="testvalue1")),
            content_type='application/json',
        )
        res_json = json.loads(str(res.data, 'utf8'))
        self.assertTrue(res.status_code == 201)
        self.assertTrue('id' in res_json)
        self.assertTrue('Location' in res.headers)

        testid1 = res_json["id"]

        res = self.client.delete('/task/')
        res_json = json.loads(str(res.data, 'utf8'))
        self.assertTrue(res.status_code == 400)
        self.assertTrue('errormsg' in res_json)
        self.assertTrue('id is required' in res_json['errormsg'])

        res = self.client.delete('/task/000000000000000000000000')
        res_json = json.loads(str(res.data, 'utf8'))
        self.assertTrue(res.status_code == 404)
        self.assertTrue('errormsg' in res_json)
        self.assertTrue('task doesn\'t exists' in res_json['errormsg'])

        res = self.client.delete('/task/'+testid1)
        res_json = json.loads(str(res.data, 'utf8'))
        self.assertTrue(res.status_code == 200)

        res = self.client.get('/task/'+testid1)
        res_json = json.loads(str(res.data, 'utf8'))
        self.assertTrue(res.status_code == 404)
        self.assertTrue('errormsg' in res_json)
        self.assertTrue('task doesn\'t exists' in res_json['errormsg'])

    def test_misc(self):

        res = self.client.get('/')
        res_json = json.loads(str(res.data, 'utf8'))
        self.assertTrue(res.status_code == 200)
        self.assertTrue(len(res_json) == 0)

if __name__ == '__main__':
    unittest.main()
