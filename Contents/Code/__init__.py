from datetime import datetime
import content
import config

TITLE  = "BBC iPlayer"
PREFIX = "/video/iplayer"

BBC_URL              = "http://www.bbc.co.uk"
BBC_FEED_URL         = "http://feeds.bbc.co.uk"
BBC_LIVE_TV_URL      = "%s/iplayer/tv/%%s/watchlive" % BBC_URL
BBC_SEARCH_URL       = "%s/iplayer/search?q=%%s&page=%%s" % BBC_URL
BBC_SEARCH_TV_URL    = BBC_SEARCH_URL + "&filter=tv"
BBC_SEARCH_RADIO_URL = BBC_SEARCH_URL + "&filter=radio"

RE_SEARCH      = Regex('episodeRegistry\\.addData\\((.*?)\\);', Regex.IGNORECASE | Regex.DOTALL)
RE_ORDER       = Regex('class="cta-add-to-favourites" href="pid-(.*?)"')
RE_SEARCH_NEXT = Regex('title="Next page"')

ART_DEFAULT  = "art-default.jpg"
ART_WALL     = "art-wall.jpg"
ICON_DEFAULT = "icon-default.png"
ICON_SEARCH  = "icon-search.png"
ICON_PREFS   = "icon-prefs.png"

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

MAX_RSS_ITEMS_PER_PAGE = 25

##########################################################################################
def Start():
    ObjectContainer.art = R(ART_DEFAULT)
    ObjectContainer.title1 = TITLE

    DirectoryObject.art = R(ART_DEFAULT)
    DirectoryObject.thumb = R(ICON_DEFAULT)

    InputDirectoryObject.art = R(ART_DEFAULT)
    InputDirectoryObject.thumb = R(ICON_SEARCH)

    PrefsObject.art = R(ART_DEFAULT)
    PrefsObject.thumb = R(ICON_PREFS)

    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-agent'] = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.11) Gecko/20101012 Firefox/3.6.11"

##########################################################################################
@handler(PREFIX, TITLE, art = ART_DEFAULT, thumb = ICON_DEFAULT)
def MainMenu():
    oc = ObjectContainer()
    
    oc.add(DirectoryObject(key=Callback(VideosFromRSS, title="TV Highlights", url=BBC_FEED_URL + "/iplayer/highlights/tv"), title="TV Highlights"))
    oc.add(DirectoryObject(key=Callback(VideosFromRSS, title="Radio Highlights", url=BBC_FEED_URL + "/iplayer/highlights/radio"), title="Radio Highlights"))
    oc.add(DirectoryObject(key=Callback(VideosFromRSS, title="Most Popular TV", url=BBC_FEED_URL + "/iplayer/popular/tv"), title="Most Popular TV"))
    oc.add(DirectoryObject(key=Callback(VideosFromRSS, title="Most Popular Radio", url=BBC_FEED_URL + "/iplayer/popular/radio"), title="Most Popular Radio"))
    oc.add(DirectoryObject(key=Callback(TVChannels), title="TV Channels"))
    oc.add(DirectoryObject(key=Callback(RadioStations), title="Radio Stations"))
    oc.add(DirectoryObject(key=Callback(Categories), title="Categories"))
    oc.add(DirectoryObject(key=Callback(Formats), title="Formats"))
    oc.add(DirectoryObject(key=Callback(AToZ), title="A-Z"))
    oc.add(InputDirectoryObject(key = Callback(Search, search_url=BBC_SEARCH_TV_URL), title="Search TV", prompt="Search TV"))
    oc.add(InputDirectoryObject(key = Callback(Search, search_url=BBC_SEARCH_RADIO_URL), title="Search Radio", prompt="Search Radio"))

    return oc

##########################################################################################
@route(PREFIX + "/TVChannels")
def TVChannels():
    oc = ObjectContainer(title2="TV Channels")
    for channel_id in content.ordered_tv_channels:
        channel = content.tv_channels[channel_id] 
        thumb = Resource.ContentsOfURLWithFallback(url=channel.thumb_url, fallback=ICON_DEFAULT)
        oc.add(DirectoryObject(key=Callback(Channel, tv=True, channel_id=channel_id), title=channel.title, thumb=thumb))
    return oc
    
##########################################################################################
@route(PREFIX + "/RadioStations")
def RadioStations():
    oc = ObjectContainer(title2="Radio Stations")
    for channel_id in content.ordered_radio_channels:
        channel = content.radio_channels[channel_id] 
        thumb = Resource.ContentsOfURLWithFallback(url=channel.thumb_url, fallback=ICON_DEFAULT)
        oc.add(DirectoryObject(key=Callback(Channel, tv=False, channel_id=channel_id), title=channel.title, thumb=thumb))
    return oc

##########################################################################################
@route(PREFIX + "/Categories")
def Categories(channel_id=None, thumb=None):
    oc = ObjectContainer(title2="Categories")
    for category in content.categories:
        oc.add(DirectoryObject(key=Callback(Category, category_id=category.id, channel_id=channel_id), title=category.title, thumb=thumb))
    return oc
    
##########################################################################################
@route(PREFIX + "/Formats")
def Formats(channel_id=None, thumb=None):
    oc = ObjectContainer(title2="Formats")
    for format in content.formats:
        oc.add(DirectoryObject(key=Callback(VideosFromJSONEpisodeList, title=format.title, url=format.url(channel_id)), title=format.title, thumb=thumb))
    return oc
    
##########################################################################################
@route(PREFIX + "/AToZ")
def AToZ():
    oc = ObjectContainer(title2="A - Z")
    for code in range(ord('a'), ord('z') + 1):
        letter = chr(code)
        oc.add(DirectoryObject(key=Callback(VideosFromRSS, title=letter.upper(), url=BBC_FEED_URL + "/iplayer/atoz/%s/list" % letter), title=letter.upper()))
    return oc

##########################################################################################
@route(PREFIX + "/Category")
def Category(category_id, channel_id=None):
    category = content.category[category_id]
    oc = ObjectContainer(title1=category.title)
    
    if channel_id:
        return VideosFromJSONEpisodeList(title=category.title, url=category.genre_url(channel_id + "/programmes"))
    else:
        oc.add(DirectoryObject(key=Callback(VideosFromRSS, title="%s TV Highlights" % category.title, url=category.highlights_url(tv=True)), title="TV Highlights"))
        oc.add(DirectoryObject(key=Callback(VideosFromRSS, title="%s Radio Highlights" % category.title, url=category.highlights_url(tv=False)), title="Radio Highlights"))
        oc.add(DirectoryObject(key=Callback(VideosFromRSS, title="Popular %s TV" % category.title, url=category.popular_url(tv=True)), title="Most Popular TV"))
        oc.add(DirectoryObject(key=Callback(VideosFromRSS, title="Popular %s Radio" % category.title, url=category.popular_url(tv=False)), title="Most Popular Radio"))
        oc.add(DirectoryObject(key=Callback(VideosFromJSONEpisodeList, title="All programmes", url=category.genre_url(channel_id="programmes")), title="All programmes"))
        oc.add(DirectoryObject(key=Callback(VideosFromJSONEpisodeList, title="TV programmes", url=category.genre_url(channel_id="tv/programmes")), title="TV programmes"))
        oc.add(DirectoryObject(key=Callback(VideosFromJSONEpisodeList, title="Radio programmes", url=category.genre_url(channel_id="radio/programmes")), title="Radio programmes"))
        for subcategory in category.subcategories:
            oc.add(DirectoryObject(key=Callback(VideosFromRSS, title=subcategory.title, url=category.subcategory_url(subcategory.id), sort=True), title=subcategory.title))
        
    return oc

##########################################################################################
@route(PREFIX + "/Channel", tv = bool)
def Channel(tv, channel_id):
    if tv:
        channel = content.tv_channels[channel_id]
    else:
        channel = content.radio_channels[channel_id]
   
    oc = ObjectContainer(title1=channel.title)
    thumb = Resource.ContentsOfURLWithFallback(url=channel.thumb_url, fallback=ICON_DEFAULT)

    if channel.has_live_broadcasts():
        oc.add(VideoClipObject(url = channel.live_url(), title = "Live", thumb = thumb))

    if channel.has_highlights():
        oc.add(DirectoryObject(key=Callback(VideosFromRSS, title="Highlights", url=channel.highlights_url()), title="Highlights", thumb=thumb))
        oc.add(DirectoryObject(key=Callback(VideosFromRSS, title="Most Popular", url=channel.popular_url()), title="Most Popular", thumb=thumb))

    oc.add(DirectoryObject(key=Callback(Categories, channel_id=channel_id, thumb=thumb), title="Categories", thumb=thumb))

    if channel.has_live_broadcasts():
        # Add the last week's worth of schedules
        oc.add(DirectoryObject(key=Callback(VideosFromJSONScheduleList, title=channel.title, url=channel.schedule_url + "today.json"), title="Today", thumb=thumb))
        oc.add(DirectoryObject(key=Callback(VideosFromJSONScheduleList, title=channel.title, url=channel.schedule_url + "yesterday"), title="Yesterday", thumb=thumb))
        now = datetime.today()
        for i in range (2, 7):
            date = now - Datetime.Delta(days=i)
            oc.add(DirectoryObject(key=Callback(VideosFromJSONScheduleList, title=channel.title, url="%s/%s/%s/%s.json" % (channel.schedule_url, date.year, date.month, date.day)), title=DAYS[date.weekday()], thumb=thumb))

    oc.add(DirectoryObject(key=Callback(Formats, channel_id=channel_id, thumb=thumb), title="Formats", thumb=thumb))

    return oc

##########################################################################################
@route(PREFIX + "/VideosFromRSS", offset = int)
def VideosFromRSS(title="", url=None, sort=False, offset=0):
    thumb_url = "http://node2.bbcimg.co.uk/iplayer/images/episode/%s_640_360.jpg"

    feed = RSS.FeedFromURL(url)
    if feed is None: return

    oc = ObjectContainer(title1=title)

    counter = 0
    totalEntries = len(feed.entries)

    for entry in feed.entries:
        counter = counter + 1
        
        if counter < offset + 1:
            continue
            
        thumb = thumb_url % entry["link"].split("/")[-3]
        parts = entry["title"].split(": ")

        # This seems to strip out the year on some series
        if len(parts) == 3:
            title = "%s: %s" % (parts[0], parts[2])
        else:
            title = entry["title"]

        content = HTML.ElementFromString(entry["content"][0].value)
        summary = content.xpath("p")[1].text.strip()
        # FIXME: add duration
        
        oc.add(EpisodeObject(url=entry["link"], title=title, summary=summary, thumb=thumb))
        
        # Add next page object if we exceed the max items per page
        if counter - offset >= MAX_RSS_ITEMS_PER_PAGE and totalEntries > counter:
            nextPage = (offset / MAX_RSS_ITEMS_PER_PAGE) + 2
            lastPage = (totalEntries / MAX_RSS_ITEMS_PER_PAGE) + 1
            titleNextPage = "Next page (" + str(nextPage) + "/" + str(lastPage) + ")..."
            oc.add(NextPageObject(key=Callback(VideosFromRSS, url=url, sort=sort, offset=counter), title=titleNextPage))
            return oc

    if len(oc) == 0:
        return NoProgrammesFound(oc, title)

    if sort:
        oc.objects.sort(key=lambda obj: obj.title)

    return oc

##########################################################################################
@route(PREFIX + "/VideosFromJSONEpisodeList", hd = bool)
def VideosFromJSONEpisodeList(title, url):

    # this function generates the category lists and format lists from a JSON feed
    oc = ObjectContainer(title1 = title)

    try:
        jsonObj = JSON.ObjectFromURL(url)
        if jsonObj is None: return NoProgrammesFound(oc, title)
    except:
        return NoProgrammesFound(oc, title)

    episodes = jsonObj["episodes"]
  
    for programme in episodes:
  
        thisProgramme = programme["programme"]
        displayTitles = thisProgramme["display_titles"]
        title = displayTitles["title"]
        foundSubtitle = displayTitles["subtitle"]
        pid = thisProgramme["pid"]
        short_synopsis = thisProgramme["short_synopsis"]
        
        #TODO: Hardcoded URL's(won't work for BBC HD???)
        url = config.BBC_SD_PLAYER_URL % pid
        thumb = config.BBC_SD_THUMB_URL % pid

        oc.add(EpisodeObject(url = url, title = "%s - %s" % (title, foundSubtitle), summary = short_synopsis, thumb = thumb))

    if len(oc) == 0:
        return NoProgrammesFound(oc, title)

    oc.objects.sort(key=lambda obj: obj.title)

    return oc

##########################################################################################
@route(PREFIX + "/VideosFromJSONScheduleList")
def VideosFromJSONScheduleList(title="", url=None):
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
        short_synopsis = thisProgramme["short_synopsis"]
      
        # assume unavailable unless we can find an expiry date of after now
        available = 0
        nowDate = 0
        expiryDate = 0
        if thisProgramme.has_key("media"):
            media = thisProgramme["media"]
            if media.has_key("expires"):
                nowDate = Datetime.Now()
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

##########################################################################################
@route(PREFIX + "/Search")
def Search(query, search_url, page_num = 1):
    oc = ObjectContainer(title1 = query)
    
    searchResults = HTTP.Request(search_url % (String.Quote(query),page_num)).content

    # Extract out JS object which contains program info.
    match = RE_SEARCH.search(searchResults)

    if match:
        jsonObj = JSON.ObjectFromString(match.group(1))
        if jsonObj:
            eps = jsonObj.values()

            # Try to extract out the order of the show out of the html as the JSON object is a dictionary keyed by PID which means 
            # the results order can't be guaranteed by just iterating through it.    
            epOrder = []
            for match in RE_ORDER.finditer(searchResults):
                epOrder.append(match.group(1))

            eps.sort(key=lambda ep: (ep['id'] in epOrder and (epOrder.index(ep['id']) + 1)) or 1000)

            for progInfo in eps:
                url = BBC_URL + progInfo['my_url']
                duration = int(progInfo['duration']) * 1000
                title = progInfo['complete_title']
                foundSubtitle = progInfo['masterbrand_title']
                broadcast_date = Datetime.ParseDate(progInfo['original_broadcast_datetime'].split("T")[0]).date() 
                pid = progInfo['id']
                short_synopsis = progInfo['short_synopsis']
    
                if progInfo.has_key("availability") and progInfo["availability"] == 'CURRENT':
                    oc.add(EpisodeObject(url=url, title=title, summary=short_synopsis, duration=duration, originally_available_at=broadcast_date, thumb=config.BBC_SD_THUMB_URL % pid)) 

    if len(oc) == 0:
        return NoProgrammesFound(oc, query)
    else:
        # See if we need a next button.
        if RE_SEARCH_NEXT.search(searchResults):
            oc.add(NextPageObject(key=Callback(Search, query = query, search_url = search_url, page_num = page_num + 1), title='More...'))

    return oc
    
##########################################################################################
def NoProgrammesFound(oc, title):
    oc.header  = title
    oc.message = "No programmes found."
    return oc
