import mediafile
import pylast
from beets import config, dbcore, plugins, ui
from beets.dbcore import types


class LastLovedPlugin(plugins.BeetsPlugin):
    def __init__(self):
        super().__init__()
        config["lastfm"].add(
            {
                "user": "",
                "api_key": plugins.LASTFM_KEY,
            }
        )
        config["lastfm"]["api_key"].redact = True
        field = mediafile.MediaField(
            mediafile.MP3DescStorageStyle("loved"), mediafile.StorageStyle("loved")
        )
        self.add_media_field("loved", field)
        self.item_types = {
            "loved": types.BOOLEAN,
        }

    def commands(self):
        cmd = ui.Subcommand("lastloved", help="import last.fm loved tracks")

        def func(lib, opts, args):
            num_cleared = 0
            for item in lib.items():
                if item.get("loved", False):
                    self.clear_old(item)
                    num_cleared += 1
            if num_cleared > 0:
                self._log.info(f"Removing {num_cleared} old values...")
            import_loved(lib, self._log)

        cmd.func = func
        return [cmd]

    def clear_old(self, item):
        item["loved"] = False
        item.store()
        item.write()


def import_loved(lib, log):
    user = config["lastfm"]["user"].as_str()
    if not user:
        raise ui.UserError("You must specify a username for lastloved")

    log.info("Fetching last.fm library for @{0}", user)

    track_total = 0

    loved_tracks = fetch_tracks(user, log)

    track_total = len(loved_tracks)

    log.info("Found {0} loved tracks", track_total)

    process_tracks(lib, loved_tracks, log)


def fetch_tracks(user, log):
    """JSON format:
    [
        {
            "mbid": "...",
            "artist": "...",
            "title": "...",
        }
    ]
    """
    network = pylast.LastFMNetwork(api_key=config["lastfm"]["api_key"])
    results = network.get_user(user).get_loved_tracks(limit=None)
    return [
        {
            "artist": track.track.artist.name,
            "album": (
                str(str(track.track.get_album()).split(" - ")[1:]).translate(
                    {ord(i): None for i in "[]''"}
                )
                if str(track.track.get_album())
                else None
            ),
            "title": track.track.title,
            "mbid": track.track.get_mbid(),
        }
        for track in results
    ]


def process_tracks(lib, tracks, log):
    total = len(tracks)
    total_found = 0
    total_fails = 0
    log.info("Processing {0} tracks...", total)

    for num in range(0, total):
        song = None
        trackid = tracks[num]["mbid"].strip() if tracks[num]["mbid"] else None
        artist = tracks[num]["artist"].strip() if tracks[num]["artist"] else None
        title = tracks[num]["title"].strip()
        if "album" in tracks[num]:
            album = tracks[num]["album"].strip() if tracks[num]["album"] else None

        log.debug("query: {0} - {1} ({2})", artist, title, album)

        # First try to query by MusicBrainz ID
        if trackid:
            song = lib.items(dbcore.query.MatchQuery("mb_trackid", trackid)).get()

        # If not, try with album and title
        if song is None and album:
            log.debug(
                "no match from musicbrainz, trying by album/title: {0} - {1}",
                album,
                title,
            )
            query = dbcore.AndQuery(
                [
                    dbcore.query.SubstringQuery("album", album),
                    dbcore.query.SubstringQuery("title", title),
                ]
            )
            song = lib.items(query).get()

        # If not, try just artist/title
        if song is None:
            log.debug("no album match, trying by artist/title")
            query = dbcore.AndQuery(
                [
                    dbcore.query.SubstringQuery("artist", artist),
                    dbcore.query.SubstringQuery("title", title),
                ]
            )
            song = lib.items(query).get()

        # Last resort, try just replacing to utf-8 quote
        if song is None:
            title = title.replace("'", "\u2019")
            log.debug("no title match, trying utf-8 single quote")
            query = dbcore.AndQuery(
                [
                    dbcore.query.SubstringQuery("artist", artist),
                    dbcore.query.SubstringQuery("title", title),
                ]
            )
            song = lib.items(query).get()

        if song is not None:
            log.debug(
                "match: {0} - {1} ({2})" ", updating",
                song.artist,
                song.title,
                song.album,
            )
            song["loved"] = True
            song.store()
            song.write()
            total_found += 1
        else:
            total_fails += 1
            log.info("  - No match: {0} - {1} ({2})", artist, title, album)

    if total_fails > 0:
        log.info(
            "Updated {0}/{1} tracks ({2} unknown)",
            total_found,
            total,
            total_fails,
        )

    return total_found, total_fails
