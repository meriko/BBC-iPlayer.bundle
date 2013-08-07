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
    ObjectContainer.art    = R(ART_DEFAULT)
    ObjectContainer.title1 = TITLE

    DirectoryObject.art   = R(ART_DEFAULT)
    DirectoryObject.thumb = R(ICON_DEFAULT)

    InputDirectoryObject.art   = R(ART_DEFAULT)
    InputDirectoryObject.thumb = R(ICON_SEARCH)

    PrefsObject.art   = R(ART_DEFAULT)
    PrefsObject.thumb = R(ICON_PREFS)

    HTTP.CacheTime             = CACHE_1HOUR
    HTTP.Headers['User-agent'] = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.11) Gecko/20101012 Firefox/3.6.11"

##########################################################################################
@handler(PREFIX, TITLE, art = ART_DEFAULT, thumb = ICON_DEFAULT)
def MainMenu():
    oc = ObjectContainer()
    
    title = "TV Highlights"
    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    VideosFromRSS, 
                    title = title, 
                    url = BBC_FEED_URL + "/iplayer/highlights/tv"
                ), 
            title = title
        )
    )
    
    title = "Radio Highlights"
    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    VideosFromRSS, 
                    title = title, 
                    url = BBC_FEED_URL + "/iplayer/highlights/radio"
                ),
            title = title
        )
    )
    
    title = "Most Popular TV"
    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    VideosFromRSS,
                    title = title,
                    url = BBC_FEED_URL + "/iplayer/popular/tv"
                ),
            title = title
        )
    )
    
    title = "Most Popular Radio"
    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    VideosFromRSS,
                    title = title,
                    url = BBC_FEED_URL + "/iplayer/popular/radio"
                ),
            title = title
        )
    )
    
    title = "TV Channels"
    oc.add(
        DirectoryObject(
            key = Callback(TVChannels),
            title = title
        )
    )
    
    title = "Radio Stations"
    oc.add(
        DirectoryObject(
            key = Callback(RadioStations), 
            title = title
        )
    )
    
    title = "Categories"
    oc.add(
        DirectoryObject(
            key = Callback(Categories),
            title = title
        )
    )
    
    title = "Formats"
    oc.add(
        DirectoryObject(
            key = Callback(Formats),
            title = title
        )
    )
    
    title = "A-Z"
    oc.add(
        DirectoryObject(
            key = Callback(AToZChoice),
            title = title
        )
    )
    
    title = "Search TV"
    oc.add(
        InputDirectoryObject(
            key = 
                Callback(
                    Search, 
                    search_url = BBC_SEARCH_TV_URL
                ),
                title = title, 
                prompt = title
        )
    )
    
    title = "Search Radio"
    oc.add(
        InputDirectoryObject(
            key = 
                Callback(
                    Search,
                    search_url = BBC_SEARCH_RADIO_URL
                ),
            title = title,
            prompt = title
        )
    )

    return oc

##########################################################################################
@route(PREFIX + "/TVChannels")
def TVChannels():
    oc = ObjectContainer(title2 = "TV Channels")
    
    for channel_id in content.ordered_tv_channels:
        channel = content.tv_channels[channel_id]
        
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        Channel, 
                        tv = True,
                        channel_id = channel_id
                    ),
                title = channel.title,
                summary = L(channel_id),
                thumb = channel.thumb_url
            )
        )
        
    return oc
    
##########################################################################################
@route(PREFIX + "/RadioStations")
def RadioStations():
    oc = ObjectContainer(title2 = "Radio Stations")
    
    for channel_id in content.ordered_radio_channels:
        channel = content.radio_channels[channel_id]
    
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        Channel, 
                        tv = False,
                        channel_id = channel_id
                    ),
                title = channel.title, 
                thumb = channel.thumb_url
            )
        )
        
    return oc

##########################################################################################
@route(PREFIX + "/Categories")
def Categories(channel_id = None, thumb = None):
    oc = ObjectContainer(title2 = "Categories")
    
    for category in content.categories:
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        Category,
                        category_id = category.id,
                        channel_id = channel_id
                    ),
                title = category.title,
                thumb = thumb
            )
        )
        
    return oc
    
##########################################################################################
@route(PREFIX + "/Formats")
def Formats(channel_id = None, thumb = None):
    oc = ObjectContainer(title2 = "Formats")
    
    for format in content.formats:
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        VideosFromJSONEpisodeList,
                        title = format.title,
                        url = format.url(channel_id),
                        channel_id = channel_id
                    ),
                title = format.title,
                thumb = thumb
            )
        )
        
    return oc

##########################################################################################
@route(PREFIX + "/AToZChoice")
def AToZChoice():
    oc = ObjectContainer(title2 = "A - Z")
    
    for choice in ['TV', 'Radio']:
        oc.add(
            DirectoryObject(
                key = Callback(AToZ, suffix = choice.lower()),
                title = choice
            )
        )
    
    return oc
    
##########################################################################################
@route(PREFIX + "/AToZ")
def AToZ(suffix):
    oc = ObjectContainer(title2 = "A - Z")
    
    for code in range(ord('a'), ord('z') + 1):
        letter = chr(code)
        
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        VideosFromRSS,
                        title = letter.upper(),
                        url = BBC_FEED_URL + "/iplayer/atoz/%s/list/%s" % (letter, suffix)
                    ), 
                title = letter.upper()
            )
        )
        
    return oc

##########################################################################################
@route(PREFIX + "/Category")
def Category(category_id, channel_id = None):
    category = content.category[category_id]
    oc       = ObjectContainer(title1 = category.title)
    
    if channel_id:
        return VideosFromJSONEpisodeList(
                    title = category.title,
                    url = category.genre_url(channel_id + "/programmes"),
                    channel_id = channel_id
        )
        
    else:
        title = "%s TV Highlights" % category.title
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        VideosFromRSS, 
                        title = title,
                        url = category.highlights_url(tv = True)
                    ),
                title = title
            )
        )
        
        title = "%s Radio Highlights" % category.title
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        VideosFromRSS,
                        title = title,
                        url = category.highlights_url(tv = False)
                    ),
                title = title,
            )
        )
        
        title = "Popular %s TV" % category.title
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        VideosFromRSS,
                        title = title, 
                        url = category.popular_url(tv = True)
                    ),
                title = title
            )
        )
        
        title = "Popular %s Radio" % category.title
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        VideosFromRSS,
                        title = title,
                        url = category.popular_url(tv = False)
                    ),
                title = title
            )
        )
        
        title = "All programmes"
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        VideosFromJSONEpisodeList,
                        title = title, 
                        url = category.genre_url(channel_id = "programmes")
                    ),
                title = title
            )
        )
        
        title = "TV programmes"
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        VideosFromJSONEpisodeList,
                        title = title, 
                        url = category.genre_url(channel_id = "tv/programmes")
                    ),
                title = title
            )
        )
        
        title = "Radio programmes"
        oc.add( 
            DirectoryObject(
                key = 
                    Callback(
                        VideosFromJSONEpisodeList,
                        title = title,
                        url = category.genre_url(channel_id = "radio/programmes")
                    ),
                title = "Radio programmes"
            )
        )
        
        for subcategory in category.subcategories:
            oc.add(
                DirectoryObject(
                    key = 
                        Callback(
                            VideosFromRSS,
                            title = subcategory.title,
                            url = category.subcategory_url(subcategory.id), 
                            sort = True
                        ),
                    title = subcategory.title
                )
            )
        
    return oc

##########################################################################################
@route(PREFIX + "/Channel", tv = bool)
def Channel(tv, channel_id):
    if tv:
        channel = content.tv_channels[channel_id]
    else:
        channel = content.radio_channels[channel_id]
   
    oc = ObjectContainer(title1 = channel.title)
    thumb = channel.thumb_url

    #TODO, live broadcasts
#    if channel.has_live_broadcasts():
#        oc.add(
#            VideoClipObject(url = channel.live_url(), title = "Live", thumb = thumb)
#        )

    if channel.has_highlights():
        title = "Highlights"
        oc.add(
            DirectoryObject(
                key = Callback(VideosFromRSS, title = title, url = channel.highlights_url()), 
                title = title, 
                thumb = thumb
            )
        )
        
        title = "Most Popular"
        oc.add(
            DirectoryObject(
                key = Callback(VideosFromRSS, title = title, url = channel.popular_url()),
                title = title,
                thumb = thumb
            )
        )

    oc.add(
        DirectoryObject(
            key = Callback(Categories, channel_id = channel_id, thumb = thumb), 
            title = "Categories", 
            thumb = thumb
        )
    )

    oc.add(
        DirectoryObject(
            key = Callback(Formats, channel_id = channel_id, thumb = thumb),
            title = "Formats",
            thumb = thumb
        )
    )

    if channel.has_live_broadcasts():
        # Add the last week's worth of schedules
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        VideosFromJSONScheduleList,
                        title = channel.title,
                        url = channel.schedule_url + "today.json"
                    ),
                    title = "Today",
                    thumb = thumb
            )
        )
        
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        VideosFromJSONScheduleList,
                        title = channel.title,
                        url = channel.schedule_url + "yesterday"
                    ),
                title = "Yesterday",
                thumb = thumb
            )
        )
        
        now = datetime.today()  #TODO Can't find a framework function for this?
        for i in range (2, 7):
            date = now - Datetime.Delta(days = i)
            
            oc.add(
                DirectoryObject(
                    key = 
                        Callback(
                            VideosFromJSONScheduleList,
                            title = channel.title,
                            url = "%s/%s/%s/%s.json" % (channel.schedule_url, date.year, date.month, date.day)
                        ),
                    title = DAYS[date.weekday()],
                    thumb = thumb
                )
            )

    return oc

##########################################################################################
@route(PREFIX + "/VideosFromRSS", sort = bool, offset = int)
def VideosFromRSS(title, url, sort = False, offset = 0):
    oc = ObjectContainer(title1 = title)

    try:
        feed = RSS.FeedFromURL(url)
        
        if feed is None:
            return NoProgrammesFound(oc, title)
            
    except:
        return NoProgrammesFound(oc, title)

    counter      = 0
    totalEntries = len(feed.entries)

    for entry in feed.entries:
        counter = counter + 1
        
        if counter < offset + 1:
            continue
        
        if '/hd/' in entry["href"]:
            thumb_url = config.BBC_HD_THUMB_URL
        else:
            thumb_url = config.BBC_SD_THUMB_URL
                
        thumb = thumb_url % entry["link"].split("/")[-3]

        parts = entry["title"].split(": ")

        # This seems to strip out the year on some series
        if len(parts) == 3:
            epTitle = "%s: %s" % (parts[0], parts[2])
        else:
            epTitle = entry["title"]

        content = HTML.ElementFromString(entry["content"][0].value)
        summary = content.xpath("p")[1].text.strip()
        
        oc.add(
            EpisodeObject(
                url = entry["link"],
                title = epTitle,
                summary = summary,
                thumb = thumb
            )
        )
        
        # Add next page object if we exceed the max items per page
        if counter - offset >= MAX_RSS_ITEMS_PER_PAGE and totalEntries > counter:
            nextPage = (offset / MAX_RSS_ITEMS_PER_PAGE) + 2
            lastPage = (totalEntries / MAX_RSS_ITEMS_PER_PAGE) + 1
            titleNextPage = "Next page (" + str(nextPage) + "/" + str(lastPage) + ")..."
            
            oc.add(
                NextPageObject(
                    key = 
                        Callback(
                            VideosFromRSS,
                            title = title, 
                            url = url,
                            sort = sort,
                            offset = counter
                        ),
                    title = titleNextPage
                )
            )
            return oc

    if len(oc) < 1:
        return NoProgrammesFound(oc, title)

    if sort:
        oc.objects.sort(key = lambda obj: obj.title)

    return oc

##########################################################################################
@route(PREFIX + "/VideosFromJSONEpisodeList")
def VideosFromJSONEpisodeList(title, url, channel_id = None):

    # this function generates the category lists and format lists from a JSON feed
    oc = ObjectContainer(title1 = title)

    try:
        jsonObj = JSON.ObjectFromURL(url)
        
        if jsonObj is None:
            return NoProgrammesFound(oc, title)
            
    except:
        return NoProgrammesFound(oc, title)

    episodes = jsonObj["episodes"]
  
    for programme in episodes:
        thisProgramme  = programme["programme"]
        displayTitles  = thisProgramme["display_titles"]
        title          = displayTitles["title"]
        foundSubtitle  = displayTitles["subtitle"]
        
        if foundSubtitle:
            title = title + " - " + foundSubtitle
            
        pid            = thisProgramme["pid"]
        short_synopsis = thisProgramme["short_synopsis"]
        
        [player_url, thumb_url] = GetChannelURLs(channel_id)
        
        url   = player_url % pid
        thumb = thumb_url % pid

        oc.add(
            EpisodeObject(
                url = url, 
                title = title,
                summary = short_synopsis,
                thumb = thumb
            )
        )

    if len(oc) < 1:
        return NoProgrammesFound(oc, title)

    oc.objects.sort(key = lambda obj: obj.title)

    return oc

##########################################################################################
@route(PREFIX + "/VideosFromJSONScheduleList")
def VideosFromJSONScheduleList(title, url, channel_id = None):
    # this function generates the schedule lists for today / yesterday etc. from a JSON feed
    oc = ObjectContainer(title1 = title)
    
    try:
        jsonObj = JSON.ObjectFromURL(url)
        
        if jsonObj is None: 
            return NoProgrammesFound(oc, title)
    
    except:
        return NoProgrammesFound(oc, title)

    day = jsonObj["schedule"]["day"]
    
    for broadcast in day["broadcasts"]:
        start          = broadcast["start"][11:16]
        duration       = broadcast["duration"] * 1000 # in milliseconds
        thisProgramme  = broadcast["programme"]
        displayTitles  = thisProgramme["display_titles"]
        title          = displayTitles["title"]
        foundSubtitle  = displayTitles["subtitle"]
        pid            = thisProgramme["pid"]
        short_synopsis = thisProgramme["short_synopsis"]
      
        # assume unavailable unless we can find an expiry date of after now
        available  = False
        nowDate    = 0
        expiryDate = 0
        
        if thisProgramme.has_key("media"):
            media = thisProgramme["media"]
            
            if media.has_key("expires"): 
                available = True
                nowDate   = Datetime.Now()
                if media["expires"] == None:
                    # use an expiry date in the distant future
                    expiryDate = nowDate + timedelta(days = 1000)
                else:
                    # FIXME: this should be GMT and pytz, but to compare dates we need
                    # to have both dates to be offset naive, or aware
                    expiryDate = Datetime.ParseDate(media["expires"]).replace(tzinfo = None)

        if available and expiryDate > nowDate:
            [player_url, thumb_url] = GetChannelURLs(channel_id)
            
            oc.add(
                EpisodeObject( 
                    url = player_url % pid,
                    title = "%s %s" % (start, title),
                    summary = short_synopsis,
                    duration = duration,
                    thumb = thumb_url % pid
                )
            )
            
    return oc

##########################################################################################
@route(PREFIX + "/Search", page_num = int)
def Search(query, search_url, page_num = 1):
    oc = ObjectContainer(title1 = query)
    
    searchResults = HTTP.Request(search_url % (String.Quote(query), page_num)).content

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
                url            = BBC_URL + progInfo['my_url']
                duration       = int(progInfo['duration']) * 1000
                title          = progInfo['complete_title']
                foundSubtitle  = progInfo['masterbrand_title']
                broadcast_date = Datetime.ParseDate(progInfo['original_broadcast_datetime'].split("T")[0]).date() 
                pid            = progInfo['id']
                short_synopsis = progInfo['short_synopsis']
    
                if progInfo.has_key("availability") and progInfo["availability"] == 'CURRENT':
                    oc.add(
                        EpisodeObject(
                            url = url,
                            title = title,
                            summary = short_synopsis,
                            duration = duration,
                            originally_available_at = broadcast_date,
                            thumb = config.BBC_SD_THUMB_URL % pid
                        )
                    ) 

    if len(oc) < 1:
        return NoProgrammesFound(oc, query)
    else:
        # See if we need a next button.
        if RE_SEARCH_NEXT.search(searchResults):
            oc.add(
                NextPageObject(
                    key = 
                        Callback(
                            Search, 
                            query = query,
                            search_url = search_url,
                            page_num = page_num + 1
                        ),
                    title = 'More...'
                )
            )

    return oc
    
##########################################################################################
def NoProgrammesFound(oc, title):
    oc.header  = title
    oc.message = "No programmes found."
    return oc

##########################################################################################    
def GetChannelURLs(channel_id):
    if channel_id and channel_id == 'bbchd':
        return [config.BBC_HD_PLAYER_URL, config.BBC_HD_THUMB_URL]
    else:
        return [config.BBC_SD_PLAYER_URL, config.BBC_SD_THUMB_URL]
