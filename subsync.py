import requests, pprint, json, argparse, re, os
from urllib.parse import urljoin
from pathlib import Path

with open("config.json", "r") as f:
    config = json.load(f)

argparser = argparse.ArgumentParser()
queries = argparser.add_argument_group("Queries")
queries.add_argument("--artist", type=str)
queries.add_argument("--album", type=str)
queries.add_argument("--playlist", type=str)
queries.add_argument("--albumid", type=str)
queries.add_argument("--playlistid", type=str)
listings = argparser.add_argument_group("List options")
listings.add_argument("--list-artists", default=False, action="store_true", help="List all artists on the server")
listings.add_argument("--list-albums", default=False, action="store_true", help="List artists albums or all albums on the server")
listings.add_argument("--list-playlists", default=False, action="store_true", help="List all playlists on the server")
_download_options = argparser.add_argument_group("Download options")
download_options = _download_options.add_mutually_exclusive_group(required=False)
download_options.add_argument("--download", "-D", action="store_true", help="Directly download files")
download_options.add_argument("--transcode", "-T", action="store_true", help="Transcode and download files")
download_options.add_argument("--m3u-only", action="store_true", help="Only write m3u files")
argparser.add_argument("--dir", "-d", type=str)
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

def download(list):
    if "album" in list["subsonic-response"]:
        listname = list["subsonic-response"]["album"]["artist"] + " - " + list["subsonic-response"]["album"]["name"]
        ulist = list["subsonic-response"]["album"]["song"]
    elif "playlist" in list["subsonic-response"]:
        listname = list["subsonic-response"]["playlist"]["name"]
        ulist = list["subsonic-response"]["playlist"]["entry"]
    if args.download:
        os.makedirs(Path("albums", listname))
        for item in ulist:
            filename, file = connection.get_binary("download", {"id": item["id"]})
            with open(Path("albums", listname, filename), "wb") as f:
                f.write(file)
                f.close
            print(filename)
    elif args.transcode:
        pass
    elif args.m3u_only:
        pass

connection = subsonic_server(config["server"])
connection.test_connection()

#Get list of all artists on the server
#request = requests.get("https://nd.rocranon.arctozo.lt/rest/getArtists?u=apitest&p=ApiTest123&v=1.16.1&c=SubSync&f=json").json()
request = connection.get_json("getArtists")
for item in request["subsonic-response"]["artists"]["index"]:
    for item2 in item["artist"]:
        artists[item2["name"]] = item2["id"]

# Print list of artists
if args.list_artists:
    pprint.pprint(artists)

if args.list_playlists:
    pprint.pprint(connection.get_json("getPlaylists"))
    

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
    album = connection.get_json("getAlbum", {"id": albumid})
    #filename, file = connection.get_binary()
    # with open("album.txt", "w", encoding="utf-8") as f:
    #     pprint.pprint(album, f)
    download(album)

#idk what to do if only album is given
if args.album and not args.artist:
    print("asdf3")

if args.playlist:
    playlists = connection.get_json("getPlaylists")
    #TODO this is probably some convoluted list comprehension
    playlists2 = {}
    for item in playlists["subsonic-response"]["playlists"]["playlist"]:
        playlists2[item["name"]] = item["id"]
    playlistid = search_dict(playlists2, args.playlist)
    playlist = connection.get_json("getPlaylist", {"id": playlistid})
    # with open("playlist.txt", "w", encoding="utf-8") as f:
    #     pprint.pprint(playlist, f)
    download(playlist)
