BBC_URL                       = "http://www.bbc.co.uk"
BBC_FEED_URL                  = "http://feeds.bbc.co.uk"
BBC_SD_PLAYER_URL             = "%s/iplayer/episode/%%s" % BBC_URL
BBC_HD_PLAYER_URL             = "%s/iplayer/episode/%%s/hd" % BBC_URL
BBC_LIVE_TV_URL               = "%s/iplayer/tv/%%s/watchlive" % BBC_URL
BBC_SD_THUMB_URL              = "http://node2.bbcimg.co.uk/iplayer/images/episode/%s_640_360.jpg"
BBC_HD_THUMB_URL              = "http://node2.bbcimg.co.uk/iplayer/images/episode/%s_832_468.jpg"
BBC_TV_CHANNEL_THUMB_URL      = "%s/iplayer/img/tv/%%s.jpg" % BBC_URL

BBC_SEARCH_URL                = "%s/iplayer/search?q=%%s&page=%%s" % BBC_URL
BBC_SEARCH_TV_URL             = BBC_SEARCH_URL + "&filter=tv"

RE_SEARCH = Regex('episodeRegistry\\.addData\\((.*?)\\);', Regex.IGNORECASE | Regex.DOTALL)
RE_SEARCH_NEXT = Regex('title="Next page"')
RE_ORDER = Regex('class="cta-add-to-favourites" href="pid-(.*?)"')
RE_PID = Regex('iplayer/episode/([^/$]{8})')
