from django.shortcuts import render
from django.http import HttpResponse
from main import LogIn, Search
from models import PokeSpawns
from LocationSetter import LocationSetter
from django.views.generic import View
from django.http import JsonResponse
from django import forms
import numpy as np
import math
import time
from geopy.geocoders import GoogleV3

# Create your views here.

class PokeForm(forms.Form):
    email = forms.EmailField()
    startLocation = forms.CharField(max_length = 100)
    radius = forms.FloatField()


class MapView(View):
    template_name = 'index.html'
    accessToken, apiEndpoint, response = LogIn()

    pokeList = [1,2,3,4,5,6,7,8,9,25,26,37,38,50,51,52,53,
                54,55,56,57,58,59,63,64,65,66,67,68,74,75,76,77,
                78,79,80,83,87,88,89,92,93,94,95,96,97,104,105,106,107,
                108,109,110,111,112,113,115,124,125,126,130,131,132,
                138,139,140,141,142,143,147,148,149,150,151]

    def get(self, request):

        form = PokeForm()

        return render(request, self.template_name, {'form': form,
                                                    'pokeList':MapView.pokeList})

    def post(self, request):

        
        email = request.POST['email']
        #get the pokemon wanted from the checkboxes
        wantedPokemon = request.POST.getlist('wanted')
        #The wanted list is a list of unicode strings, need to convert to ascii and change them to ints
        for i in range(len(wantedPokemon)):
            wantedPokemon[i] = int(wantedPokemon[i].encode('ascii', 'ignore'))
        
        startLocation =request.POST['location']
        radius = request.POST['radius']
        radius =float(radius.encode('ascii', 'ignore')) #Again unicode
        grid = GetSearchGrid(startLocation, radius)
        print 'grid: ' + str(grid)
        print 'Wanted Pokemon: ' + str(wantedPokemon)

        foundPokemon = []
        seen = []
        sent = []

        #Set the time for a hour
        now = time.time()
        future = now + 3600


        while time.time() < future:
            #grid is a widthXwidthX2 Tensor. The first two dimensions is a grid of points, the third holds the
            #latitude and longitude for each point.
            for x in grid:
                #x is widthx2
                pokemonToSend = []
                for y in x:
                    #y is a vector of length 2 (AKA Long and Lat).
                    pokeList = Search(y, MapView.accessToken, MapView.apiEndpoint, MapView.response)
                    
                    #This checks for if previous iterations have seen this particular pokemon.
                    #The api this is based on used this exact method, so I'm using it.
                    #hashID is just 'spawnPointId:pokemonId' should be relatively unique.
                    for pok in pokeList:
                        if pok['hashID'] not in seen:
                            foundPokemon.append(pok)
                            seen.append(pok['hashID'])

                            #Loop Through all pokemon found this loop and if it is a wanted pokemon and the last
                            #iteration did not find this then add it to the pokemon to send and record it
                            #as having been sent
                            if (int(pok['pokeID']) in wantedPokemon)and (pok['hashID'] not in sent):
                                pokemonToSend.append(pok)
                                sent.append(pok['hashID'])
            
                #Obvious check to see if anything needs to be sent
                if len(pokemonToSend)>=1:
                    SendAlert(pokemonToSend, email)
            
                    
                    
            
           
            

            print pokemonToSend
            print foundPokemon
       

        return HttpResponse("Thanks for signing up")

def GetSearchGrid(location, radius):
    #width^2 is the number of points searched
    width = 6
    #If width equals 5 we want a range starting from -2 to 2 for the offsets
    numIncrements = int(math.floor(width/2))
    offset = np.linspace(-numIncrements, numIncrements, num = width)

    #This is to set up the change in long and lat for each point based on the radius.
    #This currently has some magic numbers and needs to be fixed.
    locator = GoogleV3()
    dLat = radius * (1/float(72)) *(.5)
    startLocation = locator.geocode(location, timeout = 10)
    dLong = math.degrees(math.asin(radius/(4*3959*math.sin(math.radians(startLocation.latitude)))))

    #locationTensor holds 2 matrices, one for long and one for lat
    locationTensor = np.zeros((width, width, 2))
    count = 0
    for matrix in locationTensor:
        matrix.T[0] = startLocation.latitude + dLat * offset
        locationTensor.T[1][count] =startLocation.longitude + dLong * offset
        count += 1

    return locationTensor

def SendAlert(pokemonToSend, email):
    locator = GoogleV3()
    from django.core.mail import send_mail
    body = 'Rare Pokemon detected! Here are the details: \n'

    for poke in pokemonToSend:
        #find the address from the long and lat
        location = locator.reverse(str(poke['long']) + ', ' + str(poke['lat']),exactly_one = True)
        #Creates the body with all the relevant info
        pokeInfo = (str(poke['pokeID']) + ' ' + str(poke['pokeName'])+ '\n' +
                        'Longitude and Latitude: ' + str(poke['long']) + ', ' + str(poke['lat']) +'\n'+
                        'Time Left: ' + str(poke['timeLeft']) + '\n')
        
        #Sometimes reverse does not return an address.
        if location != None:
            pokeInfo += 'Address: ' + str(location.address) + '\n\n'
        else:
            pokeInfo += '\n'


        body += pokeInfo

    send_mail(
        'Rare Pokemon Spotted!',
        body,
        'keamoke@gmail.com',
        [email],
        fail_silently = False)





