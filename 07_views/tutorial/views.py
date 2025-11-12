from pyramid.response import Response
from pyramid.view import view_config

# 'view_config' ini menghubungkan 'route_name'
# ke fungsi di bawahnya
@view_config(route_name='home')
def home(request):
    """View untuk halaman utama."""
    return Response('<body>Visit <a href="/howdy">hello</a></body>')

@view_config(route_name='hello')
def hello(request):
    """View untuk halaman /howdy."""
    return Response('<body>Go back <a href="/">home</a></body>')