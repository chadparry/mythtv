#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------
# Name: tmdb_api.py    Simple-to-use Python interface to TMDB's API v3
# Python Library
# Author: Raymond Wagner
# Purpose: This Python library is intended to provide a series of classes
#          and methods for search and retrieval of text metadata and image
#          URLs from TMDB.
#          Preliminary API specifications can be found at
#          http://help.themoviedb.org/kb/api/about-3
# License: Creative Commons GNU GPL v2
# (http://creativecommons.org/licenses/GPL/2.0/)
#-----------------------

__title__ = "tmdb_api - Simple-to-use Python interface to TMDB's API v3 "+\
            "(www.themoviedb.org)"
__author__ = "Raymond Wagner"
__purpose__ = """
This Python library is intended to provide a series of classes and methods
for search and retrieval of text metadata and image URLs from TMDB.
Preliminary API specifications can be found at
http://help.themoviedb.org/kb/api/about-3"""

__version__="v0.1.0"
# 0.1.0 Initial development

from util import PagedList, Datapoint, Datalist, Datadict, Element
from tmdb_exceptions import *

import json
import urllib
import urllib2
import datetime

DEBUG = False

def set_key(key):
    """
    Specify the API key to use retrieving data from themoviedb.org. This
    key must be set before any calls will function.
    """
    # MythTV key: c27cb71cff5bd76e1a7a009380562c62
    if len(key) != 32:
        raise TMDBKeyInvalid("Specified API key must be 128-bit hex")
    try:
        int(key, 16)
    except:
        raise TMDBKeyInvalid("Specified API key must be 128-bit hex")
    Request._api_key = key

class Request( urllib2.Request ):
    _api_key = None
    _base_url = "http://api.themoviedb.org/3/"

    @property
    def api_key(self):
        if self._api_key is None:
            raise TMDBKeyMissing("API key must be specified before "+\
                                 "requests can be made")
        return self._api_key

    def __init__(self, url, **kwargs):
        """Return a request object, using specified API path and arguments."""
        kwargs['api_key'] = self.api_key

        url = self._base_url + url.lstrip('/') + '?' + urllib.urlencode(kwargs)
        urllib2.Request.__init__(self, url)
        self.add_header('Accept', 'application/json')

    def open(self):
        try:
            if DEBUG:
                print 'loading '+self.get_full_url()
            return urllib2.urlopen(self)
        except urllib2.HTTPError, e:
            raise TMDBHTTPError(str(e))

    def read(self):
        return self.open().read()

    def readJSON(self):
        data = json.load(self.open())
        if 'status_code' in data:
            if data['status_code'] == 7:
                raise TMDBKeyInvalid(data['status_message'])
        if DEBUG:
            import pprint
            pprint.PrettyPrinter().pprint(data)
        return data

class Configuration( object ):
    _data = {}
    def __init__(self):
        if len(self._data) == 0:
            self._data.update(Request('configuration').readJSON())
    def get(self, key):
        return self._data.get(key)

def searchMovie(query, language='en-US'):
    res = Request('search/movie', query=query, language=language)
    return SearchResults(query, language, res.readJSON())

class SearchResults( PagedList ):
    """Stores a list of search matches."""
    @staticmethod
    def _process(data):
        for item in data['results']:
            yield Movie(raw=item)
    def _getpage(self, page):
        res = Request('search/movie', query=self.query,
                      language=self.language, page=page)
        return list(self._process(res.readJSON()))

    def __init__(self, query, language, data):
        self.query = query
        self.language = language
        super(SearchResults, self).__init__(self._process(data),
                                            data['total_results'], 20)
    def __repr__(self):
        return u"<Search Results: {0}>".format(self.query)

class Image( Element ):
    filename        = Datapoint('file_path', initarg=1, handler=lambda x: x.lstrip('/'))
    aspectratio     = Datapoint('aspect_ratio')
    height          = Datapoint('height')
    width           = Datapoint('width')
    language        = Datapoint('iso_639_1')

    def sizes(self):
        return ['original']

    def geturl(self, size='original'):
        if size not in self.sizes():
            raise TMDBImageSizeError
        url = Configuration().get('images')['base_url'].rstrip('/')
        return url+'/{0}/{1}'.format(size, self.filename)

    def __repr__(self):
        return u"<{0.__class__.__name__} '{0.filename}'>".format(self)

class Backdrop( Image ):
    def sizes(self):
        return Configuration().get('images')['backdrop_sizes']
class Poster( Image ):
    def sizes(self):
        return Configuration().get('images')['poster_sizes']
class Profile( Image ):
    def sizes(self):
        return Configuration().get('images')['profile_sizes']

class AlternateTitle( Element ):
    country     = Datapoint('iso_3166_1')
    title       = Datapoint('title')

class Cast( Element ):
    id          = Datapoint('id')
    character   = Datapoint('character')
    name        = Datapoint('name')
    profile     = Datapoint('profile_path', handler=Profile, raw=False)
    order       = Datapoint('order')

    def __repr__(self):
        return u"<{0} '{1.name}' as '{1.character}' at {2}>".\
                        format(self.__class__.__name__, self, hex(id(self)))

class Crew( Element ):
    id          = Datapoint('id')
    name        = Datapoint('name')
    job         = Datapoint('job')
    department  = Datapoint('department')
    profile     = Datapoint('profile_path', handler=Profile, raw=False)

    def __repr__(self):
        return u"<{0.__class__.__name__} '{1.name}','{1.job}'>".format(self)

class Keyword( Element ):
    id   = Datapoint('id')
    name = Datapoint('name')

    def __repr__(self):
        return u"<{0.__class__.__name__} {0.name}>".format(self)

class Release( Element ):
    certification   = Datapoint('certification')
    country         = Datapoint('iso_3166_1')
    releasedate     = Datapoint('release_date', handler=lambda x: \
                                         datetime.datetime.strptime(x, '%Y-%m-%d'))
    def __repr__(self):
        return u"<Release {0.country}, {0.releasedate}>".format(self)

class Trailer( Element ):
    name    = Datapoint('name')
    size    = Datapoint('size')
    source  = Datapoint('source')

class Translation( Element ):
    name          = Datapoint('name')
    language      = Datapoint('iso_639_1')
    englishname   = Datapoint('english_name')

class Genre( Element ):
    id      = Datapoint('id')
    name    = Datapoint('name')

class Studio( Element ):
    id      = Datapoint('id')
    name    = Datapoint('name')

class Country( Element ):
    code    = Datapoint('iso_3166_1')
    name    = Datapoint('name')

class Language( Element ):
    code    = Datapoint('iso_639_1')
    name    = Datapoint('name')

class Movie( Element ):
    id              = Datapoint('id', initarg=1)
    title           = Datapoint('title')
    originaltitle   = Datapoint('original_title')
    tagline         = Datapoint('tagline')
    overview        = Datapoint('overview')
    runtime         = Datapoint('runtime')
    budget          = Datapoint('budget')
    revenue         = Datapoint('revenue')
    releasedate     = Datapoint('release_date', handler=lambda x: \
                                         datetime.datetime.strptime(x, '%Y-%m-%d'))
    homepage        = Datapoint('homepage')
    imdb            = Datapoint('imdb_id')

    backdrop        = Datapoint('backdrop_path', handler=Backdrop, raw=False)
    poster          = Datapoint('poster_path', handler=Poster, raw=False)

    popularity      = Datapoint('popularity')
    userrating      = Datapoint('vote_average')
    votes           = Datapoint('vote_count')

    adult       = Datapoint('adult')
    collection  = Datapoint('belongs_to_collection')#, handler=Collection)
    genres      = Datalist('genres', handler=Genre)
    studios     = Datalist('production_companies', handler=Studio)
    countries   = Datalist('production_countries', handler=Country)
    languages   = Datalist('spoken_languages', handler=Language)

    def _populate(self):
        return Request('movie/{0}'.format(self.id)).readJSON()
    def _populate_titles(self):
        return Request('movie/{0}/alternate_titles'.format(self.id)).readJSON()
    def _populate_cast(self):
        return Request('movie/{0}/casts'.format(self.id)).readJSON()
    def _populate_images(self):
        return Request('movie/{0}/images'.format(self.id)).readJSON()
    def _populate_keywords(self):
        return Request('movie/{0}/keywords'.format(self.id)).readJSON()
    def _populate_releases(self):
        return Request('movie/{0}/releases'.format(self.id)).readJSON()
    def _populate_trailers(self):
        return Request('movie/{0}/trailers'.format(self.id)).readJSON()
    def _populate_translations(self):
        return Request('movie/{0}/translations'.format(self.id)).readJSON()

    alternate_titles = Datalist('titles', handler=AlternateTitle, poller=_populate_titles)
    cast             = Datalist('cast', handler=Cast, poller=_populate_cast, sort='order')
    crew             = Datalist('crew', handler=Crew, poller=_populate_cast)
    backdrops        = Datalist('backdrops', handler=Backdrop, poller=_populate_images)
    posters          = Datalist('posters', handler=Poster, poller=_populate_images)
    keywords         = Datalist('keywords', handler=Keyword, poller=_populate_keywords)
    releases         = Datadict('countries', handler=Release, poller=_populate_releases, attr='country')
    youtube_trailers = Datalist('youtube', handler=Trailer, poller=_populate_trailers)
    apple_trailers   = Datalist('quicktime', handler=Trailer, poller=_populate_trailers)
    translations     = Datalist('translations', handler=Translation, poller=_populate_translations)

    def __repr__(self):
        if self.title is not None:
            s = u"'{0}'".format(self.title)
        elif self.originaltitle is not None:
            s = u"'{0}'".format(self.originaltitle)
        else:
            s = u"'No Title'"
        if self.releasedate:
            s = u"{0} ({1})".format(s, self.releasedate.year)
        return u"<{0} {1}>".format(self.__class__.__name__, s).encode('utf-8')

class Collection( Element ):
    id       = Datapoint('id', initarg=1)
    name     = Datapoint('name')
    backdrop = Datapoint('backdrop_path', handler=Backdrop, raw=False)
    poster   = Datapoint('poster_path', handler=Poster, raw=False)
    members  = Datalist('parts', handler=Movie)

    def _populate(self):
        return Request('collection/{0}'.format(self.id)).readJSON()

Movie.collection.sethandler(Collection)

if __name__ == '__main__':
    set_key('c27cb71cff5bd76e1a7a009380562c62')
#    DEBUG = True

    banner = 'tmdb_api interactive shell.'
    import code
    try:
        import readline, rlcompleter
    except:
        pass
    else:
        readline.parse_and_bind("tab: complete")
        banner += ' TAB completion available.'
    namespace = globals().copy()
    namespace.update(locals())
    code.InteractiveConsole(namespace).interact(banner)
