class Channel(object):
    def __init__(self, title, thumb, channel_id, region_id, live_id):
        self.title = title
        self.thumb = thumb
        self.channel_id = channel_id
        self.live_id = live_id

        self.schedule_url = "http://www.bbc.co.uk/%s/programmes/schedules/" % (self.channel_id)
        if region_id:
            self.schedule_url = self.schedule_url + region_id + "/"

        thumb_url = """http://www.bbc.co.uk/iplayer/img/tv/%s.jpg"""
            
        self.thumb_url = thumb_url % self.thumb

    def has_highlights(self):
        # All TV channels have highlights
        return True

    def highlights_url(self):
        return "http://feeds.bbc.co.uk/iplayer/%s/highlights" % self.channel_id

    def popular_url(self):
        return "http://feeds.bbc.co.uk/iplayer/%s/popular" % self.channel_id

    def has_live_broadcasts(self):
        return self.live_id != None
        
    def has_scheduled_programmes(self):
        return self.live_id != None
        
    def live_url(self):
        return "http://www.bbc.co.uk/iplayer/tv/%s/watchlive" % self.live_id

tv_channels = {
    #                           title                thumb               channel_id    region_id  live_id
    'bbcone':           Channel('BBC One',           'bbc_one',          'bbcone',    'london',  'bbc_one_london'),
    'bbctwo':           Channel('BBC Two',           'bbc_two',          'bbctwo',    'england', 'bbc_two_england'),
    'bbcthree':         Channel('BBC Three',         'bbc_three',        'bbcthree',   None,     'bbc_three'),
    'bbcfour':          Channel('BBC Four',          'bbc_four',         'bbcfour',    None,     'bbc_four'),
    'cbbc':             Channel('CBBC',              'cbbc',             'cbbc',       None,     'cbbc'),
    'cbeebies':         Channel('CBeebies',          'cbeebies_1',       'cbeebies',   None,     'cbeebies'),
    'bbcnews':          Channel('BBC News Channel',  'bbc_news24',       'bbcnews',    None,     'bbc_news24'),
    'parliament':       Channel('BBC Parliament',    'bbc_parliament_1', 'parliament', None,     'bbc_parliament'),
    'bbchd':            Channel('BBC HD',            'bbc_hd_1',         'bbchd',      None,     None),
    'bbcalba':          Channel('BBC Alba',          'bbc_alba',         'bbcalba',    None,     'bbc_alba')
}
ordered_tv_channels = ['bbcone', 'bbctwo', 'bbcthree', 'bbcfour', 'cbbc', 'cbeebies', 'bbcnews', 'parliament', 'bbchd', 'bbcalba']

def slugify(string):
    slug = string.lower()
    slug = slug.replace("&", "and")
    slug = slug.replace(" ", "_")
    for char in ["'", "-", ", ", "!"]:
        slug = slug.replace(char, "")
    return slug

class Category(object):
    def __init__(self, title, subcategories):
        self.title = title
        self.id = slugify(title)
        self.subcategories = [Category(subtitle, []) for subtitle in subcategories]
        self.subcategory = dict([(category.id, category) for category in self.subcategories])

    def popular_url(self):
        return "http://feeds.bbc.co.uk/iplayer/popular/%s/tv" % self.id
            
    def highlights_url(self):
        return "http://feeds.bbc.co.uk/iplayer/highlights/%s/tv" % self.id

    def subcategory_url(self, subcategory_id):
        return "http://feeds.bbc.co.uk/iplayer/%s/%s/list" % (self.id, subcategory_id)
        
    def genre_url(self, channel_id):            
        return "http://www.bbc.co.uk/%s/genres/%s/player/episodes.json" % (channel_id, self.id)

categories = [
    Category("Children's", ["Animation", "Drama", "Entertainment & Comedy", "Factual", "Games & Quizzes", "Music", "Other"]),
    Category("Comedy", ["Music", "Satire", "Sitcoms", "Sketch", "Spoof", "Standup", "Other"]),
    Category("Drama", ["Action & Adventure", "Biographical", "Classic & Period", "Crime", "Historical", "Horror & Supernatural", "Legal & Courtroom", "Medical", "Musical", "Psychological", "Relationships & Romance", "SciFi & Fantasy", "Soaps", "Thriller", "War & Disaster", "Other"]),
    Category("Entertainment", ["Discussion & Talk Shows", "Games & Quizzes", "Makeovers", "Phone-ins", "Reality", "Talent Shows", "Variety Shows", "Other"]),
    Category("Factual", ["Antiques", "Arts, Culture & the Media", "Beauty & Style", "Cars & Motors", "Cinema", "Consumer", "Crime & Justice", "Disability", "Families & Relationships", "Food & Drink", "Health & Wellbeing", "History", "Homes & Gardens", "Life Stories", "Money", "Pets & Animals", "Politics", "Science & Nature", "Travel", "Other"]),
    Category("Learning", ["Pre-School", "5-11", "Adult", "Other"]),
    Category("Music", ["Classic Pop & Rock", "Classical", "Country", "Dance & Electronica", "Desi", "Easy Listening, Soundtracks & Musicals", "Folk", "Hip Hop, R'n'B & Dancehall", "Jazz & Blues", "Pop & Chart", "Rock & Indie", "Soul & Reggae", "World", "Other"]),
    Category("Sport", ["Boxing", "Cricket", "Cycling", "Equestrian", "Football", "Formula One", "Golf", "Horse Racing", "Motorsport", "Olympics", "Rugby League", "Rugby Union", "Tennis", "Other"])
]
category = dict([(category.id, category) for category in categories])

class Format(object):
    def __init__(self, title):
        self.title = title
        self.id = slugify(title)

    def url(self, channel_id=None):
        if channel_id:
            return "http://www.bbc.co.uk/%s/programmes/formats/%s/player/episodes.json" % (channel_id, self.id)
        else:
            return "http://www.bbc.co.uk/programmes/formats/%s/player/episodes.json" % (self.id)

formats = [
    Format("Animation"),
    Format("Appeals"),
    Format("Bulletins"),
    Format("Discussion & Talk"), 
    Format("Docudramas"), 
    Format("Documentaries"),
    Format("Films"),
    Format("Games & Quizzes"),
    Format("Magazines & Reviews"),
    Format("Makeovers"),
    Format("Performances & Events"),
    Format("Phone-ins"),
    Format("Readings"),
    Format("Reality"),
    Format("Talent Shows")
]
format = dict([(format.id, format) for format in formats])
