BBC_URL                       = "http://www.bbc.co.uk"
BBC_FEED_URL                  = "http://feeds.bbc.co.uk"
BBC_SD_PLAYER_URL             = "%s/iplayer/episode/%%s" % BBC_URL
BBC_HD_PLAYER_URL             = "%s/iplayer/episode/%%s/hd" % BBC_URL
BBC_LIVE_TV_URL               = "%s/iplayer/tv/%%s/watchlive" % BBC_URL
BBC_TV_CHANNEL_THUMB_URL      = "%s/iplayer/img/tv/%%s.jpg" % BBC_URL
BBC_THUMB_URL                 = "http://ichef.bbci.co.uk/programmeimages/%s/%s_640_360.jpg"

BBC_SEARCH_URL                = "%s/iplayer/search?q=%%s" % BBC_URL
BBC_SEARCH_TV_URL             = BBC_SEARCH_URL + "&filter=tv"

RE_ORDER = Regex('class="cta-add-to-favourites" href="pid-(.*?)"')
RE_PID = Regex('iplayer/episode/([^/$]{8})')

MP3_URL = String.Decode('aHR0cDovL29wZW4ubGl2ZS5iYmMuY28udWsvbWVkaWFzZWxlY3Rvci81L3NlbGVjdC9tZWRpYXNldC9odHRwLWljeS1tcDMtYS92cGlkLyVzL2Zvcm1hdC9wbHMucGxz')
HLS_URL = String.Decode('aHR0cDovL29wZW4ubGl2ZS5iYmMuY28udWsvbWVkaWFzZWxlY3Rvci81L3NlbGVjdC92ZXJzaW9uLzIuMC9mb3JtYXQvanNvbi9tZWRpYXNldC9hcHBsZS1pcGFkLWhscy92cGlkLyVz')

RADIO_IMG_URL = 'http://static.bbci.co.uk/radio/690/1.39/img/backgrounds/services/%s_t1.jpg'