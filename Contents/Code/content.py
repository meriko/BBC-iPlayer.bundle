from config import BBC_HD_PLAYER_URL, BBC_HD_THUMB_URL

class Channel(object):
    def __init__(self, title, summary, thumb, type, rss_channel_id, channel_id, region_id, live_id, thumb_url, player_url):
        self.title = title
        #self.summary = summary
        self.thumb = thumb
        self.type = type
        self.rss_channel_id = rss_channel_id
        self.channel_id = channel_id
        #self.region_id = region_id
        #self.live_id = live_id
        #self.thumb_url = thumb_url
        #self.player_url = player_url

        self.schedule_url = "http://www.bbc.co.uk/%s/programmes/schedules/" % (self.channel_id)
        if region_id:
            self.schedule_url = self.schedule_url + region_id + "/"

        # FIXME: thumb_id === rss_channel_id
        # FIXME: clients handcrafting schedule URL from channel_id for highlights and featured
        # above is only client of channel_id

        thumb_url  = """http://www.bbc.co.uk/iplayer/img/tv/%s.jpg"""
        self.thumb_url = thumb_url % self.thumb

    def has_highlights(self):
        return self.rss_channel_id != None


tv_channels = {
    #                           title                summary                      thumb               type  rss_channel_id     channel_id    region_id live_id            thumb_url         player_url
    'bbcone':           Channel('BBC One',           L("summary-bbc_one"),        'bbc_one',          'tv', 'bbc_one',         'bbcone',    'london',  'bbc_one_london',  None,             None),
    'bbctwo':           Channel('BBC Two',           L("summary-bbc_two"),        'bbc_two',          'tv', 'bbc_two',         'bbctwo',    'england', 'bbc_two_england', None,             None),
    'bbcthree':         Channel('BBC Three',         L("summary-bbc_three"),      'bbc_three',        'tv', 'bbc_three',       'bbcthree',   None,     'bbc_three',       None,             None),
    'bbcfour':          Channel('BBC Four',          L("summary-bbc_four"),       'bbc_four',         'tv', 'bbc_four',        'bbcfour',    None,     'bbc_four',        None,             None),
    'cbbc':             Channel('CBBC',              L("summary-cbbc"),           'cbbc',             'tv', 'cbbc',            'cbbc',       None,     'cbbc',            None,             None),
    'cbeebies':         Channel('CBeebies',          L("summary-cbeebies"),       'cbeebies_1',       'tv', 'cbeebies',        'cbeebies',   None,     'cbeebies',        None,             None),
    'bbcnews':          Channel('BBC News Channel',  L("summary-bbc_news24"),     'bbc_news24',       'tv', 'bbc_news24',      'bbcnews',    None,     'bbc_news24',      None,             None),
    'parliament':       Channel('BBC Parliament',    L("summary-bbc_parliament"), 'bbc_parliament_1', 'tv', 'bbc_parliament',  'parliament', None,     'bbc_parliament',  None,             None),
    'bbchd':            Channel('BBC HD',            None,                        'bbc_hd_1',         'tv', 'bbc_hd',          'bbchd',      None,     None,              BBC_HD_THUMB_URL, BBC_HD_PLAYER_URL),
    'bbcalba':          Channel('BBC Alba',          None,                        'bbc_alba',         'tv', 'bbc_alba',        'bbcalba',    None,     'bbc_alba',        None,             None)
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


