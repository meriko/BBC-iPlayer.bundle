from config import BBC_HD_PLAYER_URL, BBC_HD_THUMB_URL

class Channel(object):
    def __init__(self, title, thumb, channel_id, region_id):
        self.title = title
        self.thumb = thumb
        self.channel_id = channel_id

        self.schedule_url = "http://www.bbc.co.uk/%s/programmes/schedules/" % (self.channel_id)
        if region_id:
            self.schedule_url = self.schedule_url + region_id + "/"

        thumb_url  = """http://www.bbc.co.uk/iplayer/img/tv/%s.jpg"""
        self.thumb_url = thumb_url % self.thumb

    def has_highlights(self):
        # All TV channels have highlights
        return True

    def highlights_url(self):
        return "http://feeds.bbc.co.uk/iplayer/%s/popular" % self.channel_id

    def popular_url(self):
        return "http://feeds.bbc.co.uk/iplayer/%s/highlights" % self.channel_id

tv_channels = {
    #                           title                thumb               channel_id    region_id
    'bbcone':           Channel('BBC One',           'bbc_one',          'bbcone',    'london'),
    'bbctwo':           Channel('BBC Two',           'bbc_two',          'bbctwo',    'england'),
    'bbcthree':         Channel('BBC Three',         'bbc_three',        'bbcthree',   None),
    'bbcfour':          Channel('BBC Four',          'bbc_four',         'bbcfour',    None),
    'cbbc':             Channel('CBBC',              'cbbc',             'cbbc',       None),
    'cbeebies':         Channel('CBeebies',          'cbeebies_1',       'cbeebies',   None),
    'bbcnews':          Channel('BBC News Channel',  'bbc_news24',       'bbcnews',    None),
    'parliament':       Channel('BBC Parliament',    'bbc_parliament_1', 'parliament', None),
    'bbchd':            Channel('BBC HD',            'bbc_hd_1',         'bbchd',      None),
    'bbcalba':          Channel('BBC Alba',          'bbc_alba',         'bbcalba',    None)
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


