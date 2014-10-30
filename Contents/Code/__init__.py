import content

TITLE  = "BBC iPlayer"
PREFIX = "/video/iplayer"

BASE_URL = 'http://www.bbc.co.uk'
IMAGE_URL = 'http://ichef.bbci.co.uk/images/ic/640x360/%s.jpg'

RE_EPISODE = Regex("Episode ([0-9]+)")
RE_SERIES = Regex("Series ([0-9]+)")
RE_DURATION = Regex("([0-9]+) *(mins)*")

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
                    url = BASE_URL + '/iplayer'
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
                    url = BASE_URL + '/iplayer/group/most-popular'
                ),
            title = title
        )
    )
    
    title = "TV Channels"
    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    TVChannels,
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
                    url = BASE_URL + '/iplayer/a-z/'
                ),
            title = title
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
                summary = L(channel_id),
                thumb = Resource.ContentsOfURLWithFallback(channel.thumb_url)
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
                key = Callback(Highlights, title = title, url = BASE_URL + '/%s' % channel_id), 
                title = title, 
                thumb = Resource.ContentsOfURLWithFallback(thumb)
            )
        )
        
    return oc

##########################################################################################
@route(PREFIX + '/highlights')
def Highlights(title, url):
    oc = ObjectContainer(title2 = title)
    
    pageElement = HTML.ElementFromURL(url)
    items = pageElement.xpath("//*[contains(@class, 'stream-list')]/*[contains(@class, 'stream-item-editorial-promo')]")
    
    return Episodes(oc, items)

##########################################################################################
@route(PREFIX + '/mostpopular')
def MostPopular(title, url):
    oc = ObjectContainer(title2 = title)
    
    pageElement = HTML.ElementFromURL(url)
    items = pageElement.xpath("//*[contains(@class, 'iplayer-list')]/*[contains(@class, 'list-item')]")
    
    return Episodes(oc, items)

##########################################################################################
def Episodes(oc, items):
    for item in items:
        url = item.xpath(".//a/@href")[0]
        
        if not url.startswith("http"):
            url = BASE_URL + url
            
        title = item.xpath(".//a/@title")[0]
        
        try:
            index = int(RE_EPISODE.search(title).groups()[0])
        except:
            index = None
            
        try:
            season = int(RE_SERIES.search(title).groups()[0])
        except:
            season = None
            
        thumb = item.xpath(".//img/@src")[1]
        summary = ''.join(item.xpath(".//*[@class='synopsis']//text()")).strip()
        
        try:
            originally_available_at = Datetime.ParseDate(item.xpath(".//*[@class='release']/text()")[0].split(":")[1].strip()).date()
        except:
            originally_available_at = None
            
        try:
            duration = int(RE_DURATION.search(''.join(item.xpath(".//*[@class='duration']/text()"))).groups()[0]) * 60 * 1000
        except:
            duration = None
        
        oc.add(
            EpisodeObject(
                url = url,
                title = title,
                index = index,
                season = season,
                thumb = Resource.ContentsOfURLWithFallback(thumb),
                summary = summary,
                originally_available_at = originally_available_at,
                duration = duration
            )
        )
    
    if len(oc) < 1:
        oc.header = "Sorry"
        oc.message = "Could not find any content"
    
    return oc

##########################################################################################
@route(PREFIX + '/categories')
def Categories(title):
    oc = ObjectContainer(title2 = title)
    
    pageElement = HTML.ElementFromURL(BASE_URL + '/iplayer')
    
    for item in pageElement.xpath("//*[@class='categories-container']//a[@class='stat']"): 
        url = item.xpath("./@href")[0]
        
        if not "/iplayer/categories" in url:
            continue
        
        if not url.startswith("http"):
            url = BASE_URL + url
            
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
    
    for code in range(ord('a'), ord('z') + 1):
        letter = chr(code)
        
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
    
    for item in pageElement.xpath("//*[@id='atoz-content']//a[@class='tleo']"):
        url = item.xpath("./@href")[0]
        
        if not "/iplayer/brand" in url:
            continue
        
        if not url.startswith("http"):
            url = BASE_URL + url
            
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
        pageElement = HTML.ElementFromURL(BASE_URL + '/programmes/%s/episodes/player' % brand)
    except:
        pageElement = None
    
    if pageElement:
        for item in pageElement.xpath("//*[contains(@class, 'programmes-page')]//*[contains(@typeof, 'Episode')]"):
            url = item.xpath(".//*[@property='video']/a/@resource")[0]
            
            if not url.startswith("http"):
                url = BASE_URL + url
                
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

    

  
