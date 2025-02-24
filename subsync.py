import requests, pprint, json, argparse
from urllib.parse import urljoin

with open("config.json", "r") as f:
    config = json.load(f)

argparser = argparse.ArgumentParser()
argparser.add_argument("--artist", type=str)
argparser.add_argument("--album", type=str)
argparser.add_argument("--albumid", type=str)
argparser.add_argument("--artists", default=False, action="store_true")
argparser.add_argument("--albums", default=False, action="store_true")
args = argparser.parse_args()

artists = {}
albums = {}

class subsonic_server():
    def __init__(self, server):
        self.serverurl = urljoin(server["host"], 'rest/')
        self.port = server["port"]
        self.username = server["username"]
        self.password = server["password"]
        self.parameters = {
            "u": self.username,
            "p": self.password,
            "v": "1.16.1",
            "c": "SubSync"
        }

    def test_connection(self):
        params = self.parameters
        params["f"] = "json"
        request = requests.get(self.serverurl + "ping", params=params).json()
        pprint.pprint(request)
    
    def get_json(self, endpoint, params = {}):
        params = self.parameters | params
        print(params)
        request = requests.get(self.serverurl + endpoint, params=params).json()
        return request


def get_albums_byartist(artistid):
    albums = {}
    #request = requests.get("https://nd.rocranon.arctozo.lt/rest/getArtist?id=" + str(artistid) + "&u=apitest&p=ApiTest123&v=1.16.1&c=SubSync&f=json").json()
    request = connection.get_json("getArtist", {"id": str(artistid)})
    #pprint.pprint(request)
    for item in request["subsonic-response"]["artist"]["album"]:
        albums[item["name"]] = item["id"]
    return albums

connection = subsonic_server(config["server"])
connection.test_connection()

#Get list of all artists on the server
#request = requests.get("https://nd.rocranon.arctozo.lt/rest/getArtists?u=apitest&p=ApiTest123&v=1.16.1&c=SubSync&f=json").json()
request = connection.get_json("getArtists")
for item in request["subsonic-response"]["artists"]["index"]:
    for item2 in item["artist"]:
        artists[item2["name"]] = item2["id"]

# Print list of artists
if args.artists == True:
    pprint.pprint(artists)

# Print out albums by artist
if args.artist and not args.album:
    albums = get_albums_byartist(artists[args.artist])
    pprint.pprint(albums)

# Download based on artist and album name
if args.artist and args.album:
    albums = get_albums_byartist(artists[args.artist])
    albumid = albums[args.album]
    print(albumid)

#idk what to do if only album is given
if args.album and not args.artist:
    print("asdf3")