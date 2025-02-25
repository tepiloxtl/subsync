import json, argparse
from subsync import subsync_download

with open("config.json", "r") as f:
    config = json.load(f)

argparser = argparse.ArgumentParser()
queries = argparser.add_argument_group("Queries")
queries.add_argument("--artist", type=str)
queries.add_argument("--album", type=str)
queries.add_argument("--playlist", type=str)
queries.add_argument("--albumid", type=str, help="[NYI]")
queries.add_argument("--playlistid", type=str, help = "[NYI]")
listings = argparser.add_argument_group("List options")
listings.add_argument("--list-artists", default=False, action="store_true", help="List all artists on the server")
listings.add_argument("--list-albums", default=False, action="store_true", help="[NYI]List artists albums or all albums on the server")
listings.add_argument("--list-playlists", default=False, action="store_true", help="List all playlists on the server")
download_options = argparser.add_argument_group("Download options")
download_options_ex = download_options.add_mutually_exclusive_group(required=False)
download_options_ex.add_argument("--download", "-D", action="store_true", help="Directly download files")
download_options_ex.add_argument("--transcode", "-T", action="store_true", help="Transcode and download files")
download_options_ex.add_argument("--m3u-only", action="store_true", help="Only write m3u files")
download_options.add_argument("--local-dir", type=str, help = "For --m3u-only, path for local library")
download_options.add_argument("--format", type=str, help = "For transcoding, name of transcoding profile on the server")
download_options.add_argument("--bitrate", type=str, help = "For transcoding, optional, bitrate")
argparser.add_argument("--dir", "-d", type=str, help = "[NYI]")
args = argparser.parse_args()

subsync_download.run(config, args)