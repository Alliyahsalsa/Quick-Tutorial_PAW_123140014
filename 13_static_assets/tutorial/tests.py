import unittest
from pyramid import testing
import webtest 

class TutorialViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_home(self):
        from tutorial.views import TutorialViews 
        request = testing.DummyRequest()
        inst = TutorialViews(request) 
        response = inst.home()        
        self.assertEqual(response['name'], 'Home View')

    def test_hello(self):
        from tutorial.views import TutorialViews 
        request = testing.DummyRequest()
        inst = TutorialViews(request) 
        response = inst.hello()       
        self.assertEqual(response['name'], 'Hello View')

class TutorialFunctionalTests(unittest.TestCase):
    def setUp(self):
        from tutorial import main
        app = main({})
        from webtest import TestApp 
        self.testapp = TestApp(app)

    def test_home(self):
        res = self.testapp.get('/', status=200)
        self.assertIn(b'<h1>Hi Home View', res.body)

    def test_hello(self):
        res = self.testapp.get('/howdy', status=200)
        self.assertIn(b'<h1>Hi Hello View', res.body)

    # INI TES BARU (dari Gambar)
    def test_css(self):
        res = self.testapp.get('/static/app.css', status=200)
        self.assertIn(b'body', res.body)