import content
import config

TITLE  = "BBC iPlayer"
PREFIX = "/video/iplayer"

RE_EPISODE = Regex("Episode ([0-9]+)")
RE_EPISODE_ALT = Regex("Series [0-9]+ *: *([0-9]+)\.")
RE_SERIES = Regex("Series ([0-9]+)")
RE_DURATION = Regex("([0-9]+) *(mins)*")

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

RE_FILE = Regex('File1=(https?://.+)')

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
                    Highlights,
                    title = title,
                    url = config.BBC_URL + '/iplayer'
                ),
            title = title
        )
    )
    
    title = "Most Popular"
    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    MostPopular,
                    title = title,
                    url = config.BBC_URL + '/iplayer/group/most-popular'
                ),
            title = title
        )
    )

    title = "Live TV"
    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    Live,
                    title = title
                ),
            title = title
        )
    )
    
    title = "Live Radio"
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    LiveRadio,
                    title = title
                ),
            title = title
        )
    )
    
    title = "Categories"
    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    Categories,
                    title = title
                ),
            title = title
        )
    )
    
    title = "A-Z"
    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    AToZ,
                    title = title,
                    url = config.BBC_URL + '/iplayer/a-z/'
                ),
            title = title
        )
    )

    channels_oc = TVChannels(title = "TV Channels")
    for object in channels_oc.objects:
        oc.add(object)
  
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
@route(PREFIX + '/live')
def Live(title):
    oc = ObjectContainer(title2 = title)
    
    for channel_id in content.ordered_tv_channels:
        channel = content.tv_channels[channel_id]
        
        if channel.has_live_broadcasts():
            try:
                mdo = URLService.MetadataObjectForURL(channel.live_url())
                mdo.title = channel.title + " - " + mdo.title
                
                oc.add(mdo)
            except:
                pass # Live stream not currently available
                
    if len(oc) < 1:
        return NoProgrammesFound(oc, title)
        
    return oc     

##########################################################################################
@route(PREFIX + '/liveradio')
def LiveRadio(title):
    oc = ObjectContainer(title2 = title)
    
    for station in content.ordered_radio_stations:
        station_img_id = station
        
        if station in ['bbc_radio_fourfm']:
            station_img_id = 'bbc_radio_four'

        if Client.Product in ['Plex Web', 'Plex for Xbox One'] and not Client.Platform == 'Safari':
            oc.add(
                CreatePlayableObject(
                    title = content.radio_stations[station],
                    thumb = R(station + '.png'),
                    art = config.RADIO_IMG_URL % station_img_id,
                    type = 'mp3',
                    url = config.MP3_URL % station
                )
            )
        else:
            oc.add(
                CreatePlayableObject(
                    title = content.radio_stations[station],
                    thumb = R(station + '.png'),
                    art = config.RADIO_IMG_URL % station_img_id,
                    type = 'hls',
                    url = config.HLS_URL % station
                )
            )                   

    return oc

##########################################################################################
@route(PREFIX + '/tvchannels')
def TVChannels(title):
    oc = ObjectContainer(title2 = title)
    
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
                summary = unicode(L(channel_id)),
                thumb = R("%s.png" % channel_id)
            )
        )
        
    return oc

##########################################################################################
@route(PREFIX + "/Channel")
def Channel(channel_id):
    channel = content.tv_channels[channel_id]

    oc = ObjectContainer(title1 = channel.title)

    if channel.has_live_broadcasts():
        try:
            oc.add(URLService.MetadataObjectForURL(channel.live_url()))
        except:
            pass # Live stream not currently available


    title = "Highlights"
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    Highlights,
                    title = title,
                    url = channel.highlights_url()
                ),
            title = title,
            thumb = R("%s.png" % channel_id)
        )
    )

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
                thumb = R("%s.png" % channel_id)
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
            thumb = R("%s.png" % channel_id)
        )
    )
    
    now = Datetime.Now()
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
                thumb = R("%s.png" % channel_id)
            )
        )

    return oc

##########################################################################################
@route(PREFIX + '/highlights')
def Highlights(title, url):    
    return Episodes(title, url, "//*[contains(@class, 'iplayer-stream')]//*[contains(@class, 'grid__item')]")

##########################################################################################
@route(PREFIX + '/mostpopular')
def MostPopular(title, url):
    return Episodes(title, url, "//*[contains(@class, 'iplayer-list')]/*[contains(@class, 'list-item')]")

##########################################################################################
@route(PREFIX + '/categories')
def Categories(title):
    oc = ObjectContainer(title2 = title)
    
    pageElement = HTML.ElementFromURL(config.BBC_URL + '/iplayer')
    
    for item in pageElement.xpath("//*[@class='categories-container']//a[@class='stat']"): 
        url = item.xpath("./@href")[0]
        
        if not "/iplayer/categories" in url:
            continue
        
        if not url.startswith("http"):
            url = config.BBC_URL + url
            
        title = item.xpath("./text()")[0].strip()
        
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        Highlights,
                        title = title,
                        url = url
                    ),
                title = title
            )
        )
    
    return oc
    
##########################################################################################
@route(PREFIX + "/atoz")
def AToZ(title, url):
    oc = ObjectContainer(title2 = title)

    for letter in ['0-9'] + list(map(chr, range(ord('a'), ord('z') + 1))):
        oc.add(
            DirectoryObject(
                key =
                    Callback(
                        ProgramsByLetter,
                        url = url,
                        letter = letter.lower()
                    ),
                title = letter.upper()
            )
        )

    return oc

##########################################################################################
@route(PREFIX + "/programsbyletter")
def ProgramsByLetter(url, letter):
    oc = ObjectContainer(title2 = letter.upper())
    
    pageElement = HTML.ElementFromURL(url + letter)
    
    for item in pageElement.xpath("//*[@id='atoz-content']//a[contains(@class,'tleo')]"):
        url = item.xpath("./@href")[0]
        
        if not "/iplayer/brand" in url:
            continue
        
        if not url.startswith("http"):
            url = config.BBC_URL + url
            
        title = item.xpath(".//*[@class='title']/text()")[0].strip()
        
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        Programs,
                        title = title,
                        url = url
                    ),
                title = title
            )
        )
    
    return oc
    
##########################################################################################
@route(PREFIX + "/programs")
def Programs(title, url):
    oc = ObjectContainer(title2 = title)
    
    brand = url.split("/")[-1]
    
    try:
        pageElement = HTML.ElementFromURL(config.BBC_URL + '/programmes/%s/episodes/player' % brand)
    except:
        pageElement = None
    
    if pageElement:
        for item in pageElement.xpath("//*[contains(@class, 'programmes-page')]//*[contains(@typeof, 'Episode')]"):
            url = item.xpath(".//*[@property='video']/a/@resource")[0]
            
            if not url.startswith("http"):
                url = config.BBC_URL + url
                
            title = item.xpath(".//*[contains(@class, 'programme__title')]//*[@property='name']/text()")[0].strip()
            thumb = item.xpath(".//meta[@property='image']/@content")[0]
            summary = item.xpath(".//*[contains(@class, 'programme__synopsis')]//*[@property='description']/text()")[0].strip()
            
            try:
                index = int(item.xpath(".//*[contains(@class, 'programme__synopsis')]//*[@property='position']/text()")[0].strip())
            except:
                index = None
                
            try:
                season = int(item.xpath(".//*[contains(@typeof, 'Season')]//*[@property='name']/text()")[0].strip())
            except:
                season = None
            
            oc.add(
                EpisodeObject(
                    url = url,
                    title = title,
                    index = index,
                    season = season,
                    thumb = Resource.ContentsOfURLWithFallback(thumb),
                    summary = summary
                )
            )     
            
        return oc

    else:
        # Program with only one episode available
        pageElement = HTML.ElementFromURL(url)
        
        url = pageElement.xpath("//meta[@property='og:url']/@content")[0]
        title = ''.join(pageElement.xpath("//*[@id='show-info']//*[@id='title']//text()")).strip()
        summary = ''.join(pageElement.xpath("//*[@id='show-info']//*[@id='long-description']//text()")).strip()
        
        thumb = pageElement.xpath("//meta[@property='og:image']/@content")[0]
        
        try:
            originally_available_at = Datetime.ParseDate(''.join(item.xpath("//*[@id='show-info']//*[@class='release']//text()")).split(":")[1].strip()).date()
        except:
            originally_available_at = None
            
        try:
            duration = int(RE_DURATION.search(''.join(item.xpath("//*[@id='show-info']//*[@class='duration']//text()"))).groups()[0]) * 60 * 1000
        except:
            duration = None
            
        oc.add(
            VideoClipObject(
                url = url,
                title = title,
                summary = summary,
                thumb = Resource.ContentsOfURLWithFallback(thumb),
                originally_available_at = originally_available_at,
                duration = duration
            )
        )
        
        return oc

##########################################################################################
@route(PREFIX + "/Search")
def Search(query):
    url = config.BBC_SEARCH_TV_URL % String.Quote(query)
    
    return Episodes(
        title = query,
        url = url,
        xpath = "//*[contains(@class,'iplayer-list')]//*[contains(@class,'list-item')]",
        page_num = 1
    )
 
##########################################################################################
@route(PREFIX + '/episodes', page_num = int)
def Episodes(title, url, xpath, page_num = None):
    oc = ObjectContainer(title2 = title)
    orgURL = url
    
    if page_num is not None:
        if not '?' in url:
            url = url + "?"
        else:
            url = url + "&"
            
        url = url + "page=%s" % page_num
        
    pageElement = HTML.ElementFromURL(url)
    items = pageElement.xpath(xpath)

    links = []
    for item in items:
        is_group = False
        try:
            link = item.xpath(".//a/@href")[0]

            if not ('/episode/' in link or '/group/' in link):
                continue

            is_group = '/group/' in link
            
            if is_group:
                if '-' in link.split("group")[1]:
                    continue
            
            if not link.startswith('http'):
                link = config.BBC_URL + link
        except:
            continue

        try:
            title = item.xpath(".//a/@title")[0].strip()
        except:
            title = None
        
        if not title:
            if is_group:
                try:
                    title = ''.join(item.xpath(".//a//text()")[0]).strip()
                except:
                    pass
            
            if not title:
                try:
                    title = item.xpath(".//a//*[contains(@class, 'item__subtitle')]/text()")[0].strip()
                except:
                    title = None
        
        if not title:
            try:
                if is_group:
                    title = item.xpath(".//a/strong/text()")[0].strip()
                else:
                    title = item.xpath(".//a//*[contains(@class, 'item__title')]//strong/text()")[0].strip()
            except:
                title = None
                
        if not title:
            try:
                title = item.xpath(".//a/strong/text()")[0].strip()
            except:
                title = None
                
        if not title:
            continue
                
        if link not in links:
            links.append(link)
        else:
            # Duplicate
            continue

        try:
            show = item.xpath(".//a//*[contains(@class, 'item__title')]//strong/text()")[0]
        except:
            if is_group:
                show = title
            else:
                show = None

        try:
            index = int(RE_EPISODE.search(show).groups()[0])
        except:
            index = None
            
        try:
            season = int(RE_SERIES.search(show).groups()[0])
            
            if not index:
                try:
                    index = int(RE_EPISODE_ALT.search(show).groups()[0])
                except:
                    pass
        except:
            season = None
            
        try:
            thumb = item.xpath(".//*[@class='r-image']/@data-ip-src")[0]
        except:
            thumb = None
            
        try:
            if is_group:
                summary = item.xpath(".//*[contains(@class,'item-count')]/text()")[0]
            else:
                summary = ''.join(item.xpath(".//*[@class='synopsis']//text()")).strip()
                
                if not summary:
                    try:
                        summary = item.xpath(".//*[contains(@class, 'item__overlay__desc')]/text()")[0]
                    except:
                        summary = None
                              
        except:
            summary = None
   
        try:
            originally_available_at = Datetime.ParseDate(item.xpath(".//*[@class='release']/text()")[0].split(":")[1].strip()).date()
        except:
            try:
                originally_available_at = Datetime.ParseDate(item.xpath(".//*[contains(@class, 'item__overlay__subtitle')]/text()")[0].split(":")[1]).date()
            except:
                originally_available_at = None
            
        try:
            duration = int(RE_DURATION.search(''.join(item.xpath(".//*[@class='duration']/text()"))).groups()[0]) * 60 * 1000
        except:
            try:
                duration = int(RE_DURATION.search(''.join(item.xpath(".//*[contains(@class, 'item__overlay__label')]//text()")).strip().lower()).groups()[0]) * 60 * 1000
            except:
                duration = None

        # Check if a link to more episodes exists
        link_more = item.xpath(".//*[contains(@class,'view-more-container')]/@href")
        
        if len(link_more) == 1:
            link_more = link_more[0]
            
            if not link_more.startswith("http"):
                link_more = config.BBC_URL + link_more
            
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
                            Episodes,
                            title = newTitle,
                            url = link_more,
                            xpath = xpath,
                            page_num = page_num
                        ),
                    title = newTitle,
                    thumb = Resource.ContentsOfURLWithFallback(thumb)
                )
            )


        if is_group:            
            oc.add(
                DirectoryObject(
                    key =
                        Callback(
                            Episodes,
                            title = title,
                            url = link,
                            xpath = "//*[contains(@class,'iplayer-list')]//*[contains(@class,'list-item')]",
                            page_num = page_num
                        ),
                    title = title,
                    thumb = Resource.ContentsOfURLWithFallback(thumb)
                )
            )
        
        else:
            oc.add(
                EpisodeObject(
                    url = link,
                    title = title,
                    show = show,
                    index = index,
                    season = season,
                    thumb = Resource.ContentsOfURLWithFallback(thumb),
                    summary = summary,
                    originally_available_at = originally_available_at,
                    duration = duration
                )
            )

    if len(oc) < 1:
        return NoProgrammesFound(oc, title)

    elif page_num is not None:
        # See if we need a next button.
        if len(pageElement.xpath("//*[@class='next txt']")) > 0:            
            oc.add(
                NextPageObject(
                    key = 
                        Callback(
                            Episodes,
                            title = oc.title2, 
                            url = orgURL,
                            xpath = xpath,
                            page_num = int(page_num) + 1
                        ),
                    title = 'More...'
                )
            )
        
    return oc

##########################################################################################
@route(PREFIX + "/VideosFromJSONScheduleList")
def VideosFromJSONScheduleList(title, url, channel_id = None):
    # this function generates the schedule lists for today / yesterday etc. from a JSON feed
    oc = ObjectContainer(title2 = title)
    
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
                    url = config.BBC_SD_PLAYER_URL % pid,
                    title = "%s %s" % (start, title),
                    summary = short_synopsis,
                    duration = duration,
                    thumb = Resource.ContentsOfURLWithFallback(config.BBC_THUMB_URL % (image_pid, pid))
                )
            )
            
    return oc

##########################################################################################
def NoProgrammesFound(oc, title):
    oc.header  = title
    oc.message = "No programmes found."
    return oc
    
####################################################################################################
@route(PREFIX + '/CreatePlayableObject', include_container = bool) 
def CreatePlayableObject(title, thumb, art, type, url, include_container = False):
    items = []

    if type == 'mp3':
        codec = AudioCodec.MP3
        container = Container.MP3
        bitrate = 128
        key = Callback(PlayMP3, url = url)

    else:
        codec = AudioCodec.AAC
        container = 'mpegts'
        bitrate = 320
        key = HTTPLiveStreamURL(Callback(PlayHLS, url = url))
    
    streams = [
        AudioStreamObject(
            codec = codec,
            channels = 2
        )
    ]

    items.append(
        MediaObject(
            bitrate = bitrate,
            container = container,
            audio_codec = codec,
            audio_channels = 2,
            parts = [
                PartObject(
                    key = key,
                    streams = streams
                )
            ]
        )
    )

    if type == 'mp3':
        obj = TrackObject(
                key = 
                    Callback(
                        CreatePlayableObject,
                        title = title,
                        thumb = thumb,
                        art = art,
                        type = type,
                        url = url,
                        include_container = True
                    ),
                rating_key = title,
                title = title,
                items = items,
                thumb = thumb,
                art = art
        )
    
    else:
        if Client.Platform in ['Plex Home Theater', 'Mystery 4']:
            # Some bug in PHT which can't handle TrackObject below
            obj = VideoClipObject(
                    key = 
                        Callback(
                            CreatePlayableObject,
                            title = title,
                            thumb = thumb,
                            type = type,
                            art = art,
                            url = url,
                            include_container = True
                        ),
                    rating_key = title,
                    title = title,
                    items = items,
                    thumb = thumb,
                    art = art
            )
        else:
            obj = TrackObject(
                    key = 
                        Callback(
                            CreatePlayableObject,
                            title = title,
                            thumb = thumb,
                            type = type,
                            art = art,
                            url = url,
                            include_container = True
                        ),
                    rating_key = title,
                    title = title,
                    items = items,
                    thumb = thumb,
                    art = art
            )
   
    if include_container:
        return ObjectContainer(objects = [obj])
    else:
        return obj

#################################################################################################### 
@route(PREFIX + '/PlayMP3.mp3')
def PlayMP3(url):
    return PlayAudio(url)
 
#################################################################################################### 
@route(PREFIX + '/PlayHLS.m3u8')
@indirect
def PlayHLS(url):
    
    data = JSON.ObjectFromURL(url)
    
    hls_url = data['media'][0]['connection'][0]['href']

    return IndirectResponse(
        VideoClipObject,
        key = HTTPLiveStreamURL(url = hls_url)
    )
    
#################################################################################################### 
def PlayAudio(url):
    content  = HTTP.Request(url).content
    file_url = RE_FILE.search(content)

    if file_url:
        stream_url = file_url.group(1)
        if stream_url[-1] == '/':
            stream_url += ';'
        else:
            stream_url += '/;'

        return Redirect(stream_url)
    else:
        raise Ex.MediaNotAvailable  

  
