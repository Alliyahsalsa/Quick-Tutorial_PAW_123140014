import unittest
from pyramid import testing

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