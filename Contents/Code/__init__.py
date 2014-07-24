from datetime import datetime
import content
import config

TITLE  = "BBC iPlayer"
PREFIX = "/video/iplayer"

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

MAX_RSS_ITEMS_PER_PAGE = 25

##########################################################################################
def Start():
    ObjectContainer.title1 = TITLE

    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:22.0) Gecko/20100101 Firefox/22.0"

##########################################################################################
@handler(PREFIX, TITLE)
def MainMenu():
    oc = ObjectContainer()
    
    title = "Highlights"
    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    VideosFromRSS, 
                    title = title, 
                    url = config.BBC_FEED_URL + "/iplayer/highlights/tv"
                ), 
            title = title
        )
    )
    
    title = "Most Popular"
    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    VideosFromRSS,
                    title = title,
                    url = config.BBC_FEED_URL + "/iplayer/popular/tv"
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
            key = Callback(AToZ),
            title = title
        )
    )
    
    title = "Search"
    oc.add(
        InputDirectoryObject(
            key = 
                Callback(Search),
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
                        channel_id = channel_id
                    ),
                title = channel.title,
                summary = L(channel_id),
                thumb = Resource.ContentsOfURLWithFallback(channel.thumb_url)
            )
        )
        
    return oc

##########################################################################################
@route(PREFIX + "/Categories")
def Categories(channel_id = None, thumb = ''):
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
                thumb = Resource.ContentsOfURLWithFallback(thumb)
            )
        )
        
    return oc
    
##########################################################################################
@route(PREFIX + "/Formats")
def Formats(channel_id = None, thumb = ''):
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
                thumb = Resource.ContentsOfURLWithFallback(thumb)
            )
        )
        
    return oc
    
##########################################################################################
@route(PREFIX + "/AToZ")
def AToZ():
    oc = ObjectContainer(title2 = "A - Z")
    
    for code in range(ord('a'), ord('z') + 1):
        letter = chr(code)
        
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        VideosFromRSS,
                        title = letter.upper(),
                        url = config.BBC_FEED_URL + "/iplayer/atoz/%s/list/tv" % letter
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
        title = "%s Highlights" % category.title
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        VideosFromRSS, 
                        title = title,
                        url = category.highlights_url()
                    ),
                title = title
            )
        )
        
        title = "%s Popular" % category.title
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        VideosFromRSS,
                        title = title, 
                        url = category.popular_url()
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
                        url = category.genre_url(channel_id = "tv/programmes")
                    ),
                title = title
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
@route(PREFIX + "/Channel")
def Channel(channel_id):
    channel = content.tv_channels[channel_id]

    oc = ObjectContainer(title1 = channel.title)

    thumb = channel.thumb_url

    if channel.has_live_broadcasts():
        try:
            oc.add(URLService.MetadataObjectForURL(channel.live_url()))
        except:
            pass # Live stream not currently available

    if channel.has_highlights():
        title = "Highlights"
        oc.add(
            DirectoryObject(
                key = Callback(VideosFromRSS, title = title, url = channel.highlights_url()), 
                title = title, 
                thumb = Resource.ContentsOfURLWithFallback(thumb)
            )
        )
        
        title = "Most Popular"
        oc.add(
            DirectoryObject(
                key = Callback(VideosFromRSS, title = title, url = channel.popular_url()),
                title = title,
                thumb = Resource.ContentsOfURLWithFallback(thumb)
            )
        )

    oc.add(
        DirectoryObject(
            key = Callback(Categories, channel_id = channel_id, thumb = thumb), 
            title = "Categories", 
            thumb = Resource.ContentsOfURLWithFallback(thumb)
        )
    )

    oc.add(
        DirectoryObject(
            key = Callback(Formats, channel_id = channel_id, thumb = thumb),
            title = "Formats",
            thumb = Resource.ContentsOfURLWithFallback(thumb)
        )
    )

    if channel.has_scheduled_programmes():
        # Add the last week's worth of schedules
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        VideosFromJSONScheduleList,
                        title = channel.title,
                        url = channel.schedule_url + "/today.json"
                    ),
                    title = "Today",
                    thumb = Resource.ContentsOfURLWithFallback(thumb)
            )
        )
        
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        VideosFromJSONScheduleList,
                        title = channel.title,
                        url = channel.schedule_url + "/yesterday.json"
                    ),
                title = "Yesterday",
                thumb = Resource.ContentsOfURLWithFallback(thumb)
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
                    thumb = Resource.ContentsOfURLWithFallback(thumb)
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
        
        thumb = entry["media_thumbnail"][0]["url"].replace("150_84", "640_360")
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
                thumb = Resource.ContentsOfURLWithFallback(thumb)
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
            title = title + " - " + str(foundSubtitle)
            
        pid            = thisProgramme["pid"]
        image_pid      = thisProgramme["image"]["pid"] if 'image' in thisProgramme else ''
        short_synopsis = thisProgramme["short_synopsis"] 
        
        url = GetPlayerURL(channel_id) % pid
        thumb = config.BBC_THUMB_URL % (image_pid, pid)

        oc.add(
            EpisodeObject(
                url = url, 
                title = title,
                summary = short_synopsis,
                thumb = Resource.ContentsOfURLWithFallback(thumb)
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
        image_pid      = thisProgramme["image"]["pid"] if 'image' in thisProgramme else ''
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
                    expiryDate = nowDate + Datetime.Delta(days = 1000)
                else:
                    # FIXME: this should be GMT and pytz, but to compare dates we need
                    # to have both dates to be offset naive, or aware
                    expiryDate = Datetime.ParseDate(media["expires"]).replace(tzinfo = None)

        if available and expiryDate > nowDate:
            oc.add(
                EpisodeObject( 
                    url = GetPlayerURL(channel_id) % pid,
                    title = "%s %s" % (start, title),
                    summary = short_synopsis,
                    duration = duration,
                    thumb = Resource.ContentsOfURLWithFallback(config.BBC_THUMB_URL % (image_pid, pid))
                )
            )
            
    return oc

##########################################################################################
@route(PREFIX + "/Search")
def Search(query):
    searchURL = config.BBC_SEARCH_TV_URL % String.Quote(query)
    
    return SearchResults(title = query, url = searchURL)

##########################################################################################
@route(PREFIX + "/SearchResults", page_num = int)
def SearchResults(title, url, page_num = 1):
    oc = ObjectContainer(title2 = title)

    orgURL = url
    
    if not '?' in url:
        url = url + "?"
    else:
        url = url + "&"
    
    pageElement = HTML.ElementFromURL(url + "page=%s" % page_num)
    
    for item in pageElement.xpath("//*[contains(@class,'iplayer-list')]//*[contains(@class,'list-item')]"):
        try:
            url = item.xpath(".//a/@href")[0]
            
            if not url.startswith('http'):
                url = config.BBC_URL + url
        except:
            continue
        
        try:
            title = item.xpath(".//a/@title")[0]
        except:
            continue
            
        try:
            thumb = item.xpath(".//*[@class='r-image']/@data-ip-src")[0]
        except:
            thumb = None
            
        try:
            summary = item.xpath(".//*[@class='synopsis']/text()")[0].strip()
        except:
            summary = None
            
        try:
            broadcast_date = item.xpath(".//*[@class='release']/text()")[0].strip().split("First shown: ")[1]
            originally_available_at = Datetime.ParseDate(broadcast_date).date()
        except:
            originally_available_at = None
        
        # Check if a link to more episodes exists
        link = item.xpath(".//*[@class='view-more-container stat']/@href")
        
        if len(link) == 1:
            link = link[0]
            
            if not link.startswith("http"):
                link = config.BBC_URL + link
            
            try:
                newTitle = title.split(",")[0]
                
                try:
                    noEpisodes = item.xpath(".//em/text()")[0].strip()
                    
                    newTitle = newTitle + ': %s episodes' % noEpisodes
                except:
                    pass
            except:
                pass
                
            
            
            oc.add(
                DirectoryObject(
                    key =
                        Callback(
                            SearchResults,
                            title = newTitle,
                            url = link
                        ),
                    title = newTitle,
                    thumb = Resource.ContentsOfURLWithFallback(thumb)
                )
            )
        
        else:
            oc.add(
                EpisodeObject(
                    url = url,
                    title = title,
                    thumb = Resource.ContentsOfURLWithFallback(thumb),
                    summary = summary,
                    originally_available_at = originally_available_at
                )
            )

    if len(oc) < 1:
        return NoProgrammesFound(oc, title)
    else:
        # See if we need a next button.
        if len(pageElement.xpath("//*[@class='next txt']")) > 0:
            oc.add(
                NextPageObject(
                    key = 
                        Callback(
                            SearchResults, 
                            title = title,
                            url = orgURL,
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
def GetPlayerURL(channel_id):
    if channel_id and channel_id == 'bbchd':
        return config.BBC_HD_PLAYER_URL
    else:
        return config.BBC_SD_PLAYER_URL
