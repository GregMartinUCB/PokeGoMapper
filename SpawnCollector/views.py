from django.shortcuts import render
from main import main
# Create your views here.

def GetPokemon(request):
    pokemon = main("654 Claudius, Windsor, CA")

    for poke in pokemon:
        print poke

