from django.conf.urls import url
from . import views
from SpawnCollector.views import MapView


urlpatterns = [
     url(r'^$',MapView.as_view()),
     url(r'^getPokemon$', views.GetPokemon)
     ]