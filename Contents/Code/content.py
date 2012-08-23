from config import BBC_HD_PLAYER_URL, BBC_HD_THUMB_URL

class Channel(object):
    def __init__(self, title, summary, thumb, type, rss_channel_id, thumb_id, channel_id, region_id, live_id, thumb_url, player_url):
        self.title = title
        self.summary = summary
        self.thumb = thumb
        self.type = type
        self.rss_channel_id = rss_channel_id
        self.thumb_id = thumb_id
        self.channel_id = channel_id
        self.region_id = region_id
        self.live_id = live_id
        self.thumb_url = thumb_url
        self.player_url = player_url

        self.schedule_url = "http://www.bbc.co.uk/%s/programmes/schedules/" % (self.channel_id)
        if region_id:
            self.schedule_url = self.schedule_url + self.region_id + "/"

tv_channels = {
    'bbcone':           Channel('BBC One',           L("summary-bbc_one"),        'bbc_one',          'tv', 'bbc_one',         None,              'bbcone',    'london',  'bbc_one_london',  None,             None),
    'bbctwo':           Channel('BBC Two',           L("summary-bbc_two"),        'bbc_two',          'tv', 'bbc_two',         None,              'bbctwo',    'england', 'bbc_two_england', None,             None),
    'bbcthree':         Channel('BBC Three',         L("summary-bbc_three"),      'bbc_three',        'tv', 'bbc_three',       None,              'bbcthree',   None,     'bbc_three',       None,             None),
    'bbcfour':          Channel('BBC Four',          L("summary-bbc_four"),       'bbc_four',         'tv', 'bbc_four',        None,              'bbcfour',    None,     'bbc_four',        None,             None),
    'cbbc':             Channel('CBBC',              L("summary-cbbc"),           'cbbc',             'tv', 'cbbc',            None,              'cbbc',       None,     'cbbc',            None,             None),
    'cbeebies':         Channel('CBeebies',          L("summary-cbeebies"),       'cbeebies_1',       'tv', 'cbeebies',       'cbeebies_1',       'cbeebies',   None,     'cbeebies',        None,             None),
    'bbc_news24':       Channel('BBC News Channel',  L("summary-bbc_news24"),     'bbc_news24',       'tv', 'bbc_news24',      None,              'bbc_news24', None,     'bbc_news24',      None,             None),
    'parliament':       Channel('BBC Parliament',    L("summary-bbc_parliament"), 'bbc_parliament_1', 'tv', 'bbc_parliament', 'bbc_parliament_1', 'parliament', None,     'bbc_parliament',  None,             None),
    'bbchd':            Channel('BBC HD',            None,                        'bbc_hd_1',         'tv', 'bbc_hd',         'bbc_hd_1',         'bbchd',      None,     None,              BBC_HD_THUMB_URL, BBC_HD_PLAYER_URL),
    'bbc_alba':         Channel('BBC Alba',          None,                        'bbc_alba',         'tv', 'bbc_alba',       'bbcalba',          'bbc_alba',   None,     'bbc_alba',        None,             None)
}

#categories = {
#    'childrens':        Category("Children's",    'childrens',     True),
#    'comedy':           Category("Comedy",        'comedy',        True),
#    'drama':            Category("Drama",         'drama',         True),
#    'entertainment':    Category("Entertainment", 'entertainment', True),
#    'factual':          Category("Factual",       'factual',       True),
#    'learning':         Category("Learning",      'learning',      True),
#    'music':            Category("Music",         'music',         True),
#    'news':             Category("News",          'news',          False),
#    'sport':            Category("Sport",         'sport',         True)
#}
#ordered_categories = sorted(categories.keys())
#

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
    Category("Learning", ["Pre-School", "5-11", "Adult"])
]
category = dict([(category.id, category) for category in categories])

# Category("Learning", { "preschool": "Pre-School", "511": "5-11", "adult": "..
# Category("Learning", {"Pre-School", "5-11"}

# Category.slug is 'learning", cetegory.sub[sub_slug]
# categories = dict([(cateogry.slug, category) for category in categories)

# replace ("&", "and") (" ", "_"), ("'", ""), ("-", "")


