from datetime import datetime, timedelta
import math, re

TITLE                         = "BBC iPlayer"

BBC_URL                       = "http://www.bbc.co.uk"
BBC_FEED_URL                  = "http://feeds.bbc.co.uk"
BBC_SD_PLAYER_URL             = "%s/iplayer/episode/%%s" % BBC_URL
BBC_HD_PLAYER_URL             = "%s/iplayer/episode/%%s/hd" % BBC_URL
BBC_LIVE_TV_URL               = "%s/iplayer/tv/%%s/watchlive" % BBC_URL
BBC_LIVE_RADIO_URL            = "%s/iplayer/radio/%%s/listenlive" % BBC_URL
BBC_SD_THUMB_URL              = "http://node2.bbcimg.co.uk/iplayer/images/episode/%s_640_360.jpg"
BBC_HD_THUMB_URL              = "http://node2.bbcimg.co.uk/iplayer/images/episode/%s_832_468.jpg"
BBC_RADIO_CHANNEL_THUMB_URL   = "%s/iplayer/img/radio/%%s.gif" % BBC_URL
BBC_TV_CHANNEL_THUMB_URL      = "%s/iplayer/img/tv/%%s.jpg" % BBC_URL

BBC_SEARCH_URL                = "%s/iplayer/search?q=%%s&page=%%s" % BBC_URL
BBC_SEARCH_TV_URL             = BBC_SEARCH_URL + "&filter=tv"
BBC_SEARCH_RADIO_URL          = BBC_SEARCH_URL + "&filter=radio"

RE_SEARCH = Regex('episodeRegistry\\.addData\\((.*?)\\);', Regex.IGNORECASE | Regex.DOTALL)
RE_SEARCH_NEXT = Regex('title="Next page"')

ART_DEFAULT                   = "art-default.jpg"
ART_WALL                      = "art-wall.jpg"
ICON_DEFAULT                  = "icon-default.png"
ICON_SEARCH                   = "icon-search.png"
ICON_PREFS                    = "icon-prefs.png"


def Start():
    Plugin.AddPrefixHandler("/video/iplayer", MainMenu, TITLE, ICON_DEFAULT, ART_WALL)
    Plugin.AddViewGroup("Menu", viewMode="List", mediaType="items")
    Plugin.AddViewGroup("Info", viewMode="InfoList", mediaType="items")

    ObjectContainer.art = R(ART_DEFAULT)
    ObjectContainer.view_group = "Info"
    ObjectContainer.title1 = TITLE

    DirectoryObject.art = R(ICON_DEFAULT)
    DirectoryObject.thumb = R(ICON_DEFAULT)

    InputDirectoryObject.art = R(ICON_DEFAULT)
    InputDirectoryObject.thumb = R(ICON_SEARCH)

    PrefsObject.art = R(ICON_DEFAULT)
    PrefsObject.thumb = R(ICON_PREFS)

    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-agent'] = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.11) Gecko/20101012 Firefox/3.6.11"


def MainMenu():
    oc = ObjectContainer()
    oc.add(DirectoryObject(key = Callback(TVHighlights), title = "TV Highlights"))
    oc.add(DirectoryObject(key = Callback(RadioHighlights), title = "Radio Highlights"))
    oc.add(DirectoryObject(key = Callback(PopularTV), title = "Most Popular TV"))
    oc.add(DirectoryObject(key = Callback(PopularRadio), title = "Most Popular Radio"))

    return oc


@route("/video/iplayer/tv/highlights")
def TVHighlights():
    url = BBC_FEED_URL + "/iplayer/highlights/tv" 
    return RSSListContainer(title="TV Highlights", url=url)


@route("/video/iplayer/radio/highlights")
def RadioHighlights():
    url = BBC_FEED_URL + "/iplayer/highlights/radio"
    return RSSListContainer(title="Radio Highlights", url=url)


@route("/video/iplayer/tv/popular")
def PopularTV():
    url = BBC_FEED_URL + "/iplayer/popular/tv"
    return RSSListContainer(title="Most Popular TV", url=url)


@route("/video/iplayer/radio/popular")
def PopularRadio():
    url = BBC_FEED_URL + "/iplayer/popular/radio"
    return RSSListContainer(title="Most Popular Radio", url=url)


def RSSListContainer(title="", url=None):
    thumb_url = "http://node2.bbcimg.co.uk/iplayer/images/episode/%s_640_360.jpg"

    feed = RSS.FeedFromString(url)
    if feed is None: return

    oc = ObjectContainer()

    for entry in feed.entries:
        thumb = bbc_thumb_url % entry["link"].split("/")[-3]
        parts = entry["title"].split(": ")

        # This seems to strip out the year on some TV series
        if len(parts) == 3:
            title = "%s: %s" % (parts[0], parts[2])
        else:
            title = entry["title"]

        content = HTML.ElementFromString(entry["content"][0].value)
        summary = content.xpath("p")[1].text.strip()
        oc.add(EpisodeObject(url=entry["link"], title=title, summary=summary, thumb=thumb))

    if len(oc) == 0:
        return MessageContainer(header = title, message = "No programmes found.")

    return oc
