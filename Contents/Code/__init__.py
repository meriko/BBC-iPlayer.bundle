from datetime import datetime, timedelta
import math, re
import content
import config
import times

TITLE                         = "BBC iPlayer"

BBC_URL                       = "http://www.bbc.co.uk"
BBC_FEED_URL                  = "http://feeds.bbc.co.uk"
BBC_LIVE_TV_URL               = "%s/iplayer/tv/%%s/watchlive" % BBC_URL
BBC_LIVE_RADIO_URL            = "%s/iplayer/radio/%%s/listenlive" % BBC_URL

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
    oc.add(DirectoryObject(key=Callback(TVHighlights), title="TV Highlights"))
    oc.add(DirectoryObject(key=Callback(PopularTV), title="Most Popular TV"))

    oc.add(DirectoryObject(key=Callback(TVChannels), title="TV Channels"))

    oc.add(DirectoryObject(key=Callback(Categories), title="Categories"))

    return oc

@route("/video/iplayer/tv")
def TVChannels():
    oc = ObjectContainer(title2="TV Channels")
    for channel_id in content.ordered_tv_channels:
        channel = content.tv_channels[channel_id] 
        thumb = Resource.ContentsOfURLWithFallback(url=channel.thumb_url, fallback=ICON_DEFAULT)
        oc.add(DirectoryObject(key=Callback(TVChannel, channel_id=channel_id), title=channel.title, thumb=thumb))
    return oc

@route("/video/iplayer/category")
def Categories():
    oc = ObjectContainer(title2="Categories")
    for category in content.categories:
        oc.add(DirectoryObject(key=Callback(Category, category_id=category.id), title=category.title))
    return oc

@route("/video/iplayer/category/{category_id}")
def Category(category_id):
    category = content.category[category_id]
    oc = ObjectContainer(title1=category.title)
    oc.add(DirectoryObject(key=Callback(CategoryHighlights, category_id=category_id), title="Highlights"))
    oc.add(DirectoryObject(key=Callback(CategoryPopular, category_id=category_id), title="Most Popular"))
    for subcategory in category.subcategories:
        oc.add(DirectoryObject(key=Callback(Subcategory, category_id=category_id, subcategory_id=subcategory.id), title=subcategory.title))
    return oc

@route("/video/iplayer/category/{category_id}/highlights")
def CategoryHighlights(category_id):
    category = content.category[category_id]
    return RSSListContainer(title="%s Highlights" % category.title, url=category.highlights_url())

@route("/video/iplayer/category/{category_id}/popular")
def CategoryPopular(category_id):
    category = content.category[category_id]
    return RSSListContainer(title="Popular %s" % category.title, url=category.popular_url())

@route("/video/iplayer/category/{category_id}/{subcategory_id}")
def Subcategory(category_id, subcategory_id):
    category = content.category[category_id]
    return RSSListContainer(title=category.title, url=category.subcategory_url(subcategory_id))

@route("/video/iplayer/tv/highlights")
def TVHighlights():
    url = BBC_FEED_URL + "/iplayer/highlights/tv" 
    return RSSListContainer(title="TV Highlights", url=url)

@route("/video/iplayer/tv/popular")
def PopularTV():
    url = BBC_FEED_URL + "/iplayer/popular/tv"
    return RSSListContainer(title="Most Popular TV", url=url)

@route("/video/iplayer/tv/{channel_id}")
def TVChannel(channel_id):
    channel = content.tv_channels[channel_id]
    oc = ObjectContainer(title1=channel.title)
    thumb = Resource.ContentsOfURLWithFallback(url=channel.thumb_url, fallback=ICON_DEFAULT)

    if channel.has_highlights():
        oc.add(DirectoryObject(key=Callback(TVChannelHighlights, channel_id=channel_id), title="Highlights", thumb=thumb))
        oc.add(DirectoryObject(key=Callback(TVChannelPopular, channel_id=channel_id), title="Most Popular", thumb=thumb))

    # FIXME: do we need categories/formats per channel?
    #dir.Append(Function(DirectoryItem(AddCategories, title = "Categories", subtitle = sender.itemTitle, thumb = thumb), thumb = thumb, channel_id = json_channel_id, thumb_url = thumb_url, player_url = player_url))
    #dir.Append(Function(DirectoryItem(AddFormats, title = "Formats", subtitle = sender.itemTitle, thumb = thumb), thumb = thumb, channel_id = json_channel_id, thumb_url = thumb_url, player_url = player_url))

    # Add the last week's worth of schedules
    oc.add(DirectoryObject(key=Callback(TVSchedule, for_when="today", channel_id=channel_id), title="Today", thumb=thumb))
    oc.add(DirectoryObject(key=Callback(TVSchedule, for_when="yesterday", channel_id=channel_id), title="Yesterday", thumb=thumb))
    now = datetime.today()
    for i in range (2, 7):
        date = now - timedelta(days=i)
        oc.add(DirectoryObject(key=Callback(TVScheduleForDay, channel_id=channel_id, year=date.year, month=date.month, day=date.day), title=times.days[date.weekday()], thumb=thumb))

    return oc

@route("/video/iplayer/tv/{channel_id}/popular")
def TVChannelPopular(channel_id):
    channel = content.tv_channels[channel_id]
    return RSSListContainer(title="Most Popular", url=channel.popular_url())

@route("/video/iplayer/tv/{channel_id}/highlights")
def TVChannelHighlights(channel_id):
    channel = content.tv_channels[channel_id]
    return RSSListContainer(title="Highlights", url=channel.highlights_url())

@route("/video/iplayer/tv/{channel_id}/{year}/{month}/{day}")
def TVScheduleForDay(channel_id, year, month, day):
    channel = content.tv_channels[channel_id]
    url = "%s/%s/%s/%s.json" % (channel.schedule_url, year, month, day)
    Log.Info(url)
    return JSONScheduleListContainer(title=channel.title, url=url)

@route("/video/iplayer/tv/{channel_id}/{for_when}")
def TVSchedule(channel_id, for_when):
    channel = content.tv_channels[channel_id]
    url = channel.schedule_url + for_when + ".json"
    return JSONScheduleListContainer(title=channel.title, url=url)

def RSSListContainer(title="", url=None):
    thumb_url = "http://node2.bbcimg.co.uk/iplayer/images/episode/%s_640_360.jpg"

    feed = RSS.FeedFromString(url)
    if feed is None: return

    oc = ObjectContainer(title1=title)

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
        # FIXME: add duration
        oc.add(EpisodeObject(url=entry["link"], title=title, summary=summary, thumb=thumb))

    if len(oc) == 0:
        return MessageContainer(header=title, message="No programmes found.")

    return oc

def JSONScheduleListContainer(title="", url=None):
    Log.Info("JSON")
    # this function generates the schedule lists for today / yesterday etc. from a JSON feed
    jsonObj = JSON.ObjectFromURL(url)
    if jsonObj is None: return
  
    oc = ObjectContainer(title1=title)

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
