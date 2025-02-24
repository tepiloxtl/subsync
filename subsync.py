import requests, pprint, json, argparse, re
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
        request = requests.get(self.serverurl + endpoint, params=params).json()
        return request
    
    def get_binary(self, endpoint, params = {}):
        params = self.parameters | params
        request = requests.get(self.serverurl + endpoint, params=params)
        content_type = request.headers.get('Content-Type', '').lower()
        if content_type == "application/json":
            print("Not a file")
        content_disposition = request.headers.get('Content-Disposition', '')
        filename_match = re.findall('filename="([^"]+)"', content_disposition)

        if filename_match:
            filename = filename_match[0]  # Use the filename from the header
        else:
            filename = "test"  # Use a default filename if not provided
        return filename, request.content


def get_albums_byartist(artistid):
    albums = {}
    #request = requests.get("https://nd.rocranon.arctozo.lt/rest/getArtist?id=" + str(artistid) + "&u=apitest&p=ApiTest123&v=1.16.1&c=SubSync&f=json").json()
    request = connection.get_json("getArtist", {"id": str(artistid)})
    #pprint.pprint(request)
    for item in request["subsonic-response"]["artist"]["album"]:
        albums[item["name"]] = item["id"]
    return albums

def search_dict(d, search_key):
    # First, check for an exact match
    if search_key in d:
        return d[search_key]
    
    # If no exact match, search for keys that start with the search_key (case insensitive)
    matching_keys = [key for key in d.keys() if key.lower().startswith(search_key.lower())]
    
    if not matching_keys:
        return None  # No matches found
    elif len(matching_keys) == 1:
        return d[matching_keys[0]]  # Return the value for the single matching key
    else:
        # If multiple matches, ask the user to pick one
        print("Multiple matches found. Please choose one:")
        for i, key in enumerate(matching_keys, 1):
            print(f"{i}. {key}")
        
        while True:
            try:
                choice = int(input("Enter the number of your choice: "))
                if 1 <= choice <= len(matching_keys):
                    return d[matching_keys[choice - 1]]
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

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
    artist = search_dict(artists, args.artist)
    albums = get_albums_byartist(artist)
    pprint.pprint(albums)

# Download based on artist and album name
if args.artist and args.album:
    artist = search_dict(artists, args.artist)
    albums = get_albums_byartist(artist)
    albumid = search_dict(albums, args.album)
    tracks = connection.get_json("getAlbum", {"id": albumid})
    #filename, file = connection.get_binary()
    pprint.pprint(tracks)
    for item in tracks["subsonic-response"]["album"]["song"]:
        filename, file = connection.get_binary("download", {"id": item["id"]})
        with open(filename, "wb") as f:
            f.write(file)
            f.close
        print(filename)

#idk what to do if only album is given
if args.album and not args.artist:
    print("asdf3")