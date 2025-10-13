import unittest
from app import app

class CMSTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/html; charset=utf-8")
        self.assertIn("about.md", response.get_data(as_text=True))
        self.assertIn("changes.txt", response.get_data(as_text=True))
        self.assertIn("history.txt", response.get_data(as_text=True))

    def test_file_path_found(self):
        path_list = [
            '/about.md',
            '/history.txt',
            '/changes.txt',
            ]
        for path in path_list:
            with self.client.get(path) as response:
                self.assertEqual(response.status_code, 200)

    def test_viewing_text_document(self):
        with self.client.get('/history.txt') as response:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, "text/plain; charset=utf-8")
            self.assertIn("Python 0.9.0 (initial release) is released.",
                      response.get_data(as_text=True))

    def test_viewing_markdown_document(self):
        response = self.client.get('/about.md')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')
        self.assertIn("<em>Sooooo simple</em>.", response.get_data(as_text=True))

    def test_file_does_not_exist(self):
        with self.client.get('/test_file') as response:
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.content_type, "text/html; charset=utf-8")

        with self.client.get(response.headers['Location']) as response:
            self.assertEqual(response.status_code, 200)
            self.assertIn("test_file does not exist",
                          response.get_data(as_text=True))

        with self.client.get("/") as response:
            self.assertNotIn("test_file does not exist",
                             response.get_data(as_text=True))

if __name__ == "__main__":
    unittest.main()