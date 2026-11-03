import threading
import unittest
import urllib.error
import urllib.request

from main import make_server


class TestServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server(0)  # port 0 = pick a free port
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def get(self, path):
        return urllib.request.urlopen(f"http://localhost:{self.port}{path}")

    def test_root(self):
        with self.get("/") as r:
            self.assertEqual(r.status, 200)
            self.assertEqual(r.read(), b"Welcome")

    def test_about(self):
        with self.get("/about") as r:
            self.assertEqual(r.status, 200)
            self.assertEqual(r.read(), b"Simple server built with the standard library")

    def test_not_found(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self.get("/missing")
        self.assertEqual(ctx.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
