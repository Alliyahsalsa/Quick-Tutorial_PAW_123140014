import unittest
from pyramid import testing

# Kita butuh ini untuk tes fungsional
import pytest 
import webtest

class TutorialViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    # Ini tes baru untuk view 'home'
    def test_home(self):
        from tutorial.views import home # Impor dari .views
        request = testing.DummyRequest()
        response = home(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Visit', response.body)

    # Ini tes baru untuk view 'hello'
    def test_hello(self):
        from tutorial.views import hello # Impor dari .views
        request = testing.DummyRequest()
        response = hello(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Go back', response.body)

# --- Fixture untuk Tes Fungsional ---
@pytest.fixture
def testapp():
    """Fixture untuk membuat aplikasi WebTest."""
    from tutorial import main 
    app = main({}, **{})     
    return webtest.TestApp(app)

def test_functional_home(testapp):
    res = testapp.get('/', status=200)
    assert b'Visit' in res.body # <--- BENAR

def test_functional_hello(testapp):
    res = testapp.get('/howdy', status=200)
    assert b'Go back' in res.body # <--- BENAR