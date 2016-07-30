from django.shortcuts import render
from django.http import HttpResponse
from main import LogIn, Search
from models import PokeSpawns
from LocationSetter import LocationSetter
from django.views.generic import View
from django.http import JsonResponse
# Create your views here.

class MapView(View):
    template_name = 'index.html'
    accessToken, apiEndpoint, response = LogIn()

    def get(self, request):
        return render(request, self.template_name)

def GetPokemon(request):
    
    import json
    pokemon = Search(MapView.StartLocation, MapView.accessToken, 
                     MapView.apiEndpoint, MapView.response)

    for poke in pokemon:
        print poke
    
    return JsonResponse(json.dumps(pokemon),safe = False)
