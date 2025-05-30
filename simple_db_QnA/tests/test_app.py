import unittest
from simple_db_QnA.api_main import app

class SimpleDbQnATestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_api_response_json(self):
        response = self.app.post('/ask', json={'question': 'What is your name?'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('answer', response.get_json())

    def test_api_response_html(self):
        response = self.app.post('/ask', data={'question': 'What is your name?'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'text/html')
        self.assertIn('<h1>Response</h1>', response.data.decode())

if __name__ == '__main__':
    unittest.main()