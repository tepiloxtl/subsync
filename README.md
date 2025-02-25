# syncsonic

Syncsonic currently is a cli album and playlist downloader from your own local or remote Subsonic-compatible server, and in future more proper synchronization tool as well as scrobbler from local players (using one of common interfaces) back to Subsonic server

* Python minimum version: 3.9?  
* Python tested on: 3.11  
* Tested Subsonic server: Navidrome  

## Usage

### 0. See help message

```bash
syncsonic -h
```

### 1. List all available artists on the server

```bash
syncsonic --list-artists
```

### 2. List artists albums

```bash
syncsonic --artist YonKaGor
```

### 3. Download unprocessed album and create a playlist file

```bash
syncsonic --artist YonKaGor --album "Mr. Sunfish" -D
```

### 4. Transcode and download album and create a playlist file

```bash
syncsonic --artist YonKaGor --album "Mr. Sunfish" -T --format mp3 --bitrate 320
```
* --format is required field, it's one of transcoding targets on your server
* --bitrate is optional, server will try and match your supplied bitrate

### 5. Only create a playlist file for an album

```bash
syncsonic --artist YonKaGor --album "Mr. Sunfish" --m3u-only --local-dir "X:/subsoniclib"
```
For when your Subsonic library is also available locally, requires --local-dir pointing to your library root directory. This function currently only makes sense if you have only one library directory on the server side

### 6. List all available playlists on the server

```bash
syncsonic --list-playlists
```

### 7. Download unprocessed playlist and create a playlist file

```bash
syncsonic --playlist "Music I care about" -D
```
The same rules apply for downloading (-D), transcoding (-T) or creating local playlist file only (--m3u-only)

`--artist`, `--album` and `--playlist` arguments are case-insensitive and tries to autocomplete, so you can also do
```bash
syncsonic --artist yon --album mr -D
```
If there are more than one matching options, syncsonic will ask you which to choose