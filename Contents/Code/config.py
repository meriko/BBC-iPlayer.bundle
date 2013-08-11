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
