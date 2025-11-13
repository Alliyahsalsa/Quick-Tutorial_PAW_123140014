from pyramid.config import Configurator

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    with Configurator(settings=settings) as config:
        config.include('pyramid_chameleon') 

        config.add_route('home', '/')
        config.add_route('hello', '/howdy')

        # INI BARIS BARU YANG MEMPERBAIKINYA
        config.add_static_view(name='static', path='tutorial:static')

        config.scan('.views') 
        return config.make_wsgi_app()