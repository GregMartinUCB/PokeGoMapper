import json
import pokemon_pb2
import time
import requests
import sqlite3
from ConfigParser import SafeConfigParser
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from s2sphere import *
from models import PokeSpawns

#Classes to hold methods
from LocationSetter import LocationSetter
from Profile import Profile
from Heartbeat import Heartbeat

parser = SafeConfigParser()
parser.read('SpawnCollector/config.cfg')

def LogIn():
    global pokemons 
    pokemons = json.load(open('SpawnCollector/pokemon.json'))
   
    #location = raw_input("Location: ")
    
    username = parser.get('login', 'username')
    password = parser.get('login', 'password')

    access_token = Profile.login_ptc(username, password)
    if access_token is None:
        print('[-] Wrong username/password')
        return
    print('[+] RPC Session Token: {} ...'.format(access_token[:25]))

    api_endpoint = Profile.get_api_endpoint(access_token)
    if api_endpoint is None:
        print('[-] RPC server offline')
        return
    print('[+] Received API endpoint: {}'.format(api_endpoint))

    response = Profile.get_profile(access_token, api_endpoint, None)
    if response is not None:
        print('[+] Login successful')

        payload = response.payload[0]
        profile = pokemon_pb2.ResponseEnvelop.ProfilePayload()
        profile.ParseFromString(payload)
        print('[+] Username: {}'.format(profile.profile.username))

        creation_time = datetime.fromtimestamp(int(profile.profile.creation_time)/1000)
        print('[+] You are playing Pokemon Go since: {}'.format(
            creation_time.strftime('%Y-%m-%d %H:%M:%S'),
        ))

        for curr in profile.profile.currency:
            print('[+] {}: {}'.format(curr.type, curr.amount))
    else:
        print('[-] Ooops...')
    return(access_token, api_endpoint, response)

def Search(location, access_token, api_endpoint, response):

    LocationSetter.set_location(location)
    origin = LatLng.from_degrees(LocationSetter.FLOAT_LAT, LocationSetter.FLOAT_LONG)
    pokeEntry =[]

    for i in range(20):
        original_lat = LocationSetter.FLOAT_LAT
        original_long = LocationSetter.FLOAT_LONG
        parent = CellId.from_lat_lng(LatLng.from_degrees(LocationSetter.FLOAT_LAT, LocationSetter.FLOAT_LONG)).parent(15)

        h = Heartbeat.heartbeat(api_endpoint, access_token, response)
        hs = [h]
        seen = set([])
        for child in parent.children():
            latlng = LatLng.from_point(Cell(child).get_center())
            LocationSetter.set_location_coords(latlng.lat().degrees, latlng.lng().degrees, 0)
            hs.append(Heartbeat.heartbeat(api_endpoint, access_token, response))
        LocationSetter.set_location_coords(original_lat, original_long, 0)

        visible = []

        for hh in hs:
            for cell in hh.cells:
                for wild in cell.WildPokemon:
                    hash = wild.SpawnPointId + ':' + str(wild.pokemon.PokemonId)
                    if (hash not in seen):
                        visible.append(wild)
                        seen.add(hash)

        print('')
        for cell in h.cells:
            if cell.NearbyPokemon:
                other = LatLng.from_point(Cell(CellId(cell.S2CellId)).get_center())
                diff = other - origin
                # print(diff)
                difflat = diff.lat().degrees
                difflng = diff.lng().degrees
                direction = (('N' if difflat >= 0 else 'S') if abs(difflat) > 1e-4 else '')  + (('E' if difflng >= 0 else 'W') if abs(difflng) > 1e-4 else '')
                print("Within one step of %s (%sm %s from you):" % (other, int(origin.get_distance(other).radians * 6366468.241830914), direction))
                for poke in cell.NearbyPokemon:
                    print('    (%s) %s' % (poke.PokedexNumber, pokemons[poke.PokedexNumber - 1]['Name']))

        print('') 
        for poke in visible:
            other = LatLng.from_degrees(poke.Latitude, poke.Longitude)
            diff = other - origin
            # print(diff)
            difflat = diff.lat().degrees
            difflng = diff.lng().degrees
            direction = (('N' if difflat >= 0 else 'S') if abs(difflat) > 1e-4 else '')  + (('E' if difflng >= 0 else 'W') if abs(difflng) > 1e-4 else '')
            print("(%s) %s is visible at (%s, %s) for %s seconds (%sm %s from you)" % (poke.pokemon.PokemonId, pokemons[poke.pokemon.PokemonId - 1]['Name'], poke.Latitude, poke.Longitude, poke.TimeTillHiddenMs / 1000, int(origin.get_distance(other).radians * 6366468.241830914), direction))
        
            pokeDict = {'pokeID': poke.pokemon.PokemonId, 
                        'pokeName': pokemons[poke.pokemon.PokemonId - 1]['Name'].encode('ascii','ignore'), 
                        'long':poke.Longitude, 
                        'lat': poke.Latitude,
                        'timeLeft':poke.TimeTillHiddenMs}
            pokeEntry.append(pokeDict)


        print('')
        walk = Heartbeat.getNeighbors()
        next = LatLng.from_point(Cell(CellId(walk[2])).get_center())
        #if raw_input('The next cell is located at %s. Keep scanning? [Y/n]' % next) in {'n', 'N'}:
        #    break
        LocationSetter.set_location_coords(next.lat().degrees, next.lng().degrees, 0)
    return pokeEntry

if __name__ == '__main__':
    main()
