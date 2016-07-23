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
    StartLocation = "38.555657, -122.815872"
    accessToken, apiEndpoint, response = LogIn()
    LatLongStart = [float(x) for x in StartLocation.split(', ')]

    def get(self, request):
        return render(request, self.template_name, context = self.get_context_data())

    def get_context_data(self, **kwargs):
        context = {'lat':self.LatLongStart[0],
                   'long':self.LatLongStart[1]}
        
        return context

def GetPokemon(request):
    import json
    
    pokemon = Search(MapView.StartLocation, MapView.accessToken, 
                     MapView.apiEndpoint, MapView.response)

    for poke in pokemon:
        print poke



    return JsonResponse(json.dumps(pokemon),safe = False)
