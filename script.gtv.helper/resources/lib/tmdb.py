import requests
import xbmc
import xbmcaddon
import json

class TMDBHelper:
    def __init__(self):
        self.addon = xbmcaddon.Addon()
        self.api_key = self.addon.getSetting('tmdb_api_key')
        self.base_url = 'https://api.themoviedb.org/3'
        self.language = xbmc.getLanguage(xbmc.ISO_639_1)

    def _make_request(self, endpoint, params=None):
        """Make a request to TMDB API"""
        if not params:
            params = {}
        params['api_key'] = self.api_key
        params['language'] = self.language

        try:
            response = requests.get(f'{self.base_url}/{endpoint}', params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            xbmc.log(f'TMDB Helper: Error making request: {str(e)}', xbmc.LOGERROR)
            return None

    def get_items(self, content_type, category):
        """Get items from TMDB based on content type and category"""
        endpoint = ''
        if content_type == 'movies':
            if category == 'trending':
                endpoint = 'trending/movie/week'
            elif category == 'popular':
                endpoint = 'movie/popular'
            elif category == 'top_rated':
                endpoint = 'movie/top_rated'
            elif category == 'now_playing':
                endpoint = 'movie/now_playing'
            elif category == 'upcoming':
                endpoint = 'movie/upcoming'
        elif content_type == 'tv':
            if category == 'trending':
                endpoint = 'trending/tv/week'
            elif category == 'popular':
                endpoint = 'tv/popular'
            elif category == 'top_rated':
                endpoint = 'tv/top_rated'
            elif category == 'on_the_air':
                endpoint = 'tv/on_the_air'
            elif category == 'airing_today':
                endpoint = 'tv/airing_today'

        if not endpoint:
            return None

        data = self._make_request(endpoint)
        if not data or 'results' not in data:
            return None

        # Format items for Kodi
        items = []
        for item in data['results']:
            kodi_item = self._format_item(item, content_type)
            if kodi_item:
                items.append(kodi_item)

        return json.dumps(items)

    def _format_item(self, item, content_type):
        """Format TMDB item for Kodi display"""
        base_image_url = 'https://image.tmdb.org/t/p/w500'
        
        if content_type == 'movies':
            return {
                'title': item.get('title', ''),
                'year': item.get('release_date', '')[:4],
                'plot': item.get('overview', ''),
                'rating': item.get('vote_average', 0),
                'poster': f"{base_image_url}{item.get('poster_path', '')}" if item.get('poster_path') else '',
                'fanart': f"{base_image_url}{item.get('backdrop_path', '')}" if item.get('backdrop_path') else '',
                'tmdb_id': item.get('id', ''),
                'mediatype': 'movie'
            }
        else:  # TV Shows
            return {
                'title': item.get('name', ''),
                'year': item.get('first_air_date', '')[:4],
                'plot': item.get('overview', ''),
                'rating': item.get('vote_average', 0),
                'poster': f"{base_image_url}{item.get('poster_path', '')}" if item.get('poster_path') else '',
                'fanart': f"{base_image_url}{item.get('backdrop_path', '')}" if item.get('backdrop_path') else '',
                'tmdb_id': item.get('id', ''),
                'mediatype': 'tvshow'
            }