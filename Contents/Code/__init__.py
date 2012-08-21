from datetime import datetime, timedelta
import math, re
import content
import config
import times

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

    oc.add(DirectoryObject(key = Callback(TVChannels), title = "TV Channels"))

    return oc


@route("/video/iplayer/tv/highlights")
def TVHighlights():
    url = BBC_FEED_URL + "/iplayer/highlights/tv" 
    return RSSListContainer(title="TV Highlights", url=url)


@route("/video/iplayer/tv/highlights/{channel_id}")
def TVChannelHighlights(channel_id):
    url = "%s/iplayer/%s/highlights" % (BBC_FEED_URL, channel_id)
    return RSSListContainer(title="Highlights", url=url)


@route("/video/iplayer/radio/highlights")
def RadioHighlights():
    url = BBC_FEED_URL + "/iplayer/highlights/radio"
    return RSSListContainer(title="Radio Highlights", url=url)


@route("/video/iplayer/tv/popular")
def PopularTV():
    url = BBC_FEED_URL + "/iplayer/popular/tv"
    return RSSListContainer(title="Most Popular TV", url=url)


@route("/video/iplayer/tv/popular/{channel_id}")
def TVChannelHighlights(channel_id):
    url = "%s/iplayer/%s/popular" % (BBC_FEED_URL, channel_id)
    return RSSListContainer(title="Most Popular", url=url)


@route("/video/iplayer/radio/popular")
def PopularRadio():
    url = BBC_FEED_URL + "/iplayer/popular/radio"
    return RSSListContainer(title="Most Popular Radio", url=url)


@route("/video/iplayer/tv/channels")
def TVChannels():
    oc = ObjectContainer(title2="TV Channels")
    for (channel_id, channel) in content.tv_channels.items():
        oc.add(DirectoryObject(key='/video/iplayer/tv/channels/%s' % channel_id, title=channel.title))
    return oc

@route("/video/iplayer/tv/{channel_id}/schedule/today")
def TVScheduleToday(channel_id):
    channel = content.tv_channels[channel_id]
    url = channel.schedule_url + "today.json"
    Log.Debug(url)
    return JSONScheduleListContainer(url=url) 

# FIXME: tv/{channel_id}
@route("/video/iplayer/tv/channels/{channel_id}")
def TVChannel(channel_id):
    channel = content.tv_channels[channel_id]
    oc = ObjectContainer(title1=channel.title)

    # FIXME: TVChannel, LiveChannel, RadioChannel with some VideoObject
    if channel.type == "tv":
        if channel.thumb_id == None:
            thumb = BBC_TV_CHANNEL_THUMB_URL % channel.rss_channel_id
        else:
            thumb = BBC_TV_CHANNEL_THUMB_URL % channel.thumb_id
    else:
        if channel.thumb_id == None:
            thumb = BBC_RADIO_CHANNEL_THUMB_URL % channel.rss_channel_id
        else:
            thumb = BBC_RADIO_CHANNEL_THUMB_URL % channel.thumb_id

    # No URL service found for http://www.bbc.co.uk/iplayer/tv/bbc_two_england/watchlive
    #if channel.live_id != None:
    #    if channel.type == "tv":
    #        oc.add(VideoClipObject(url = BBC_LIVE_TV_URL % channel.live_id, title = "On Now", thumb = thumb))
    #    else:
    #        oc.add(VideoClipObject(url = BBC_LIVE_RADIO_URL % channel.live_id, title = "On Now", thumb = thumb))

    # FIXME: if channel has highlights
    if channel.rss_channel_id != None:
        # FIXME: tv/channel/highlights instead
        oc.add(DirectoryObject(key="/video/iplayer/tv/highlights/%s" % channel_id, title="Highlights"))
        oc.add(DirectoryObject(key="/video/iplayer/tv/popular/%s" % channel_id, title="Most Popular"))

    #dir.Append(Function(DirectoryItem(AddCategories, title = "Categories", subtitle = sender.itemTitle, thumb = thumb), thumb = thumb, channel_id = json_channel_id, thumb_url = thumb_url, player_url = player_url))
    oc.add(DirectoryObject(key="/video/iplayer/tv/%s/schedule/today" % channel_id, title="Today"))
    #dir.Append(Function(DirectoryItem(JSONScheduleListContainer, title = "Yesterday", subtitle = sender.itemTitle, thumb = thumb), url = "http://www.bbc.co.uk/%s/programmes/schedules/%syesterday.json" % (json_channel_id, json_region_id_path), subtitle = sender.itemTitle, thumb_url = thumb_url, player_url = player_url))
    #now = datetime.today()
    #oneDay = timedelta(days = 1)
    #for i in range (2, 7):
    #    thisDate = now - (i * oneDay)
    #    dir.Append(Function(DirectoryItem(JSONScheduleListContainer, WeekdayName(thisDate) + " " + str(thisDate.day) + " " + MonthName(thisDate), subtitle = sender.itemTitle, thumb = thumb), url = "http://www.bbc.co.uk/%s/programmes/schedules/%s%s/%s/%s.json" % (json_channel_id, json_region_id_path, thisDate.year, thisDate.month, thisDate.day), subtitle = sender.itemTitle, thumb_url = thumb_url, player_url = player_url))
    #dir.Append(Function(DirectoryItem(AddFormats, title = "Formats", subtitle = sender.itemTitle, thumb = thumb), thumb = thumb, channel_id = json_channel_id, thumb_url = thumb_url, player_url = player_url))

    return oc

def RSSListContainer(title="", url=None):
    thumb_url = "http://node2.bbcimg.co.uk/iplayer/images/episode/%s_640_360.jpg"

    feed = RSS.FeedFromString(url)
    if feed is None: return

    oc = ObjectContainer()

    for entry in feed.entries:
        thumb = thumb_url % entry["link"].split("/")[-3]
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

def JSONScheduleListContainer(url = None):
    # this function generates the schedule lists for today / yesterday etc. from a JSON feed

    jsonObj = JSON.ObjectFromURL(url)
    if jsonObj is None: return
  
    oc = ObjectContainer()

    day = jsonObj["schedule"]["day"]
  
    for broadcast in day["broadcasts"]:
        start = broadcast["start"][11:16]
        duration = broadcast["duration"] * 1000 # in milliseconds
        thisProgramme = broadcast["programme"]
        displayTitles = thisProgramme["display_titles"]
        title = displayTitles["title"]
        foundSubtitle = displayTitles["subtitle"]
        pid = thisProgramme["pid"]
        short_synopsis = thisProgramme["short_synopsis"] + "\n\n" + "Duration: " + times.DurationAsString(duration)
      
        # assume unavailable unless we can find an expiry date of after now
        available = 0
        nowDate = 0
        expiryDate = 0
        if thisProgramme.has_key("media"):
            media = thisProgramme["media"]
            if media.has_key("expires"):
                nowDate = datetime.now()
                available = 1
                if media["expires"] == None:
                    # use an expiry date in the distant future
                    expiryDate = nowDate + timedelta(days = 1000)
                else:
                    # FIXME: this should be GMT and pytz, but to compare dates we need
                    # to have both dates to be offset naive, or aware
                    expiryDate = Datetime.ParseDate(media["expires"]).replace(tzinfo=None)


        if available == 1 and expiryDate > nowDate:
            player_url = config.BBC_HD_PLAYER_URL
            thumb_url = config.BBC_HD_THUMB_URL
            oc.add(EpisodeObject(url=player_url % pid, title = "%s %s" % (start, title), summary = short_synopsis, duration = duration, thumb = thumb_url % pid))
    return oc
