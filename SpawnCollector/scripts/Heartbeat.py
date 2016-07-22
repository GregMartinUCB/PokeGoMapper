import pokemon_pb2
import time
from s2sphere import *
from LocationSetter import LocationSetter
from google.protobuf.internal import encoder
from Profile import Profile


class Heartbeat:
    @staticmethod
    def heartbeat(api_endpoint, access_token, response):
        m4 = pokemon_pb2.RequestEnvelop.Requests()
        m = pokemon_pb2.RequestEnvelop.MessageSingleInt()
        m.f1 = int(time.time() * 1000)
        m4.message = m.SerializeToString()
        m5 = pokemon_pb2.RequestEnvelop.Requests()
        m = pokemon_pb2.RequestEnvelop.MessageSingleString()
        m.bytes = "05daf51635c82611d1aac95c0b051d3ec088a930"
        m5.message = m.SerializeToString()

        walk = sorted(Heartbeat.getNeighbors())

        m1 = pokemon_pb2.RequestEnvelop.Requests()
        m1.type = 106
        m = pokemon_pb2.RequestEnvelop.MessageQuad()
        m.f1 = ''.join(map(Heartbeat.encode, walk))
        m.f2 = "\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
        m.lat =  LocationSetter.COORDS_LATITUDE
        m.long = LocationSetter.COORDS_LONGITUDE
        m1.message = m.SerializeToString()
        response = Profile.get_profile(
            access_token,
            api_endpoint,
            response.unknown7,
            m1,
            pokemon_pb2.RequestEnvelop.Requests(),
            m4,
            pokemon_pb2.RequestEnvelop.Requests(),
            m5)
        payload = response.payload[0]
        heartbeat = pokemon_pb2.ResponseEnvelop.HeartbeatPayload()
        heartbeat.ParseFromString(payload)
        return heartbeat

    @staticmethod
    def getNeighbors():
        origin = CellId.from_lat_lng(LatLng.from_degrees(LocationSetter.FLOAT_LAT, LocationSetter.FLOAT_LONG)).parent(15)
        walk = [origin.id()]
        # 10 before and 10 after
        next = origin.next()
        prev = origin.prev()
        for i in range(10):
            walk.append(prev.id())
            walk.append(next.id())
            next = next.next()
            prev = prev.prev()
        return walk

    @staticmethod
    def encode(cellid):
        output = []
        encoder._VarintEncoder()(output.append, cellid)
        return ''.join(output)