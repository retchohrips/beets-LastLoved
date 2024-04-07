# beets-LastLoved

Plugin for [beets](https://beets.io) to import loved tracks from [last.fm](https://last.fm).

## Dependencies

- [pylast](https://github.com/pylast/pylast)

## Setup

Clone somewhere and configure beets:

```yaml
pluginpath:
  - /cloned/path/beetsplug
plugins: lastloved
lastfm:
  user: yourname
```

## Using

Just run `beet lastloved`! This will add a new field, `loved`, to your database and files. It also automatically deletes the old `loved` field on a new run, so that un-loved songs will update. I like to use this in conjunction with [smartplaylist](https://docs.beets.io/en/latest/plugins/smartplaylist.html) to make a "favorites" playlist:

```yaml
smartplaylist:
  playlists:
    - name: favorites.m3u
      query: "loved:True"
```

### Song Matching

This works by fetching your loved tracks from last.fm, then queries your beets database for the a few fields, in decreasing priortiy:

- MusicBrains track ID
- Title and Album
- Title and Artist

If these all fail, the plugin will alert you which songs it failed to match.

## Credits

This plugin is based on the [lastimport](https://docs.beets.io/en/latest/plugins/lastimport.html) plugin that is included with beets.
