from django.shortcuts import render
from main import LogIn, Search
from models import PokeSpawns
from LocationSetter import LocationSetter
# Create your views here.

def GetPokemon(request):
    points = 9
    accessToken, apiEndpoint, response = LogIn()

    StartLocation = "38.555657, -122.815872"
    LatLongStart = [float(x) for x in StartLocation.split(', ')]
    #locations = []

    #for i in range(points):
        
    pokemon = Search(StartLocation, accessToken, apiEndpoint, response)
    
    

    for poke in pokemon:

        print poke

    return render(request, 'index.html', context = {
                 'lat' :LatLongStart[0],
                 'long':LatLongStart[1],
                 'pokemon': pokemon} )

