import pokemon_pb2
from LocationSetter import LocationSetter
import requests
import json
import re
import time


DEBUG = False

class Profile:

    API_URL = 'https://pgorelease.nianticlabs.com/plfe/rpc'
    LOGIN_URL = 'https://sso.pokemon.com/sso/login?service=https%3A%2F%2Fsso.pokemon.com%2Fsso%2Foauth2.0%2FcallbackAuthorize'
    LOGIN_OAUTH = 'https://sso.pokemon.com/sso/oauth2.0/accessToken'

    SESSION = requests.session()
    SESSION.headers.update({'User-Agent': 'Niantic App'})
    SESSION.verify = False

    @staticmethod
    def get_profile(access_token, api, useauth, *reqq):
        req = pokemon_pb2.RequestEnvelop()

        req1 = req.requests.add()
        req1.type = 2
        if len(reqq) >= 1:
            req1.MergeFrom(reqq[0])

        req2 = req.requests.add()
        req2.type = 126
        if len(reqq) >= 2:
            req2.MergeFrom(reqq[1])

        req3 = req.requests.add()
        req3.type = 4
        if len(reqq) >= 3:
            req3.MergeFrom(reqq[2])

        req4 = req.requests.add()
        req4.type = 129
        if len(reqq) >= 4:
            req4.MergeFrom(reqq[3])

        req5 = req.requests.add()
        req5.type = 5
        if len(reqq) >= 5:
            req5.MergeFrom(reqq[4])

        return Profile.api_req(api, access_token, req, useauth = useauth)

    @staticmethod
    def api_req(api_endpoint, access_token, *mehs, **kw):
        try:
            p_req = pokemon_pb2.RequestEnvelop()
            p_req.rpc_id = 1469378659230941192

            p_req.unknown1 = 2

            p_req.latitude, p_req.longitude, p_req.altitude = LocationSetter.get_location_coords()

            p_req.unknown12 = 989

            if 'useauth' not in kw or not kw['useauth']:
                p_req.auth.provider = 'ptc'
                p_req.auth.token.contents = access_token
                p_req.auth.token.unknown13 = 14
            else:
                p_req.unknown11.unknown71 = kw['useauth'].unknown71
                p_req.unknown11.unknown72 = kw['useauth'].unknown72
                p_req.unknown11.unknown73 = kw['useauth'].unknown73

            for meh in mehs:
                p_req.MergeFrom(meh)

            protobuf = p_req.SerializeToString()

            r = Profile.SESSION.post(api_endpoint, data=protobuf, verify=False)

            p_ret = pokemon_pb2.ResponseEnvelop()
            p_ret.ParseFromString(r.content)

            if DEBUG:
                print("REQUEST:")
                print(p_req)
                print("Response:")
                print(p_ret)
                print("\n\n")

            print("Sleeping for 1 seconds to get around rate-limit.")
            time.sleep(.4)
            return p_ret
        except Exception as e:
            if DEBUG:
                print(e)
            return None
        
    @staticmethod
    def login_ptc(username, password):
        print('[!] login for: {}'.format(username))
        head = {'User-Agent': 'niantic'}
        r = Profile.SESSION.get(Profile.LOGIN_URL, headers=head)
        jdata = json.loads(r.content)
        data = {
            'lt': jdata['lt'],
            'execution': jdata['execution'],
            '_eventId': 'submit',
            'username': username,
            'password': password,
        }
        r1 = Profile.SESSION.post(Profile.LOGIN_URL, data=data, headers=head)

        ticket = None
        try:
            ticket = re.sub('.*ticket=', '', r1.history[0].headers['Location'])
        except Exception as e:
            if DEBUG:
                print(r1.json()['errors'][0])
            return None

        data1 = {
            'client_id': 'mobile-app_pokemon-go',
            'redirect_uri': 'https://www.nianticlabs.com/pokemongo/error',
            'client_secret': 'w8ScCUXJQc6kXKw8FiOhd8Fixzht18Dq3PEVkUCP5ZPxtgyWsbTvWHFLm2wNY0JR',
            'grant_type': 'refresh_token',
            'code': ticket,
        }
        r2 = Profile.SESSION.post(Profile.LOGIN_OAUTH, data=data1)
        access_token = re.sub('&expires.*', '', r2.content)
        access_token = re.sub('.*access_token=', '', access_token)
        return access_token

    @staticmethod
    def get_api_endpoint(access_token, api = API_URL):
        p_ret = Profile.get_profile(access_token, api, None)
        try:
            return ('https://%s/rpc' % p_ret.api_url)
        except:
            return None

