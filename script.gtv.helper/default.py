import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from resources.lib.tmdb import TMDBHelper

def main():
    # Get arguments passed to script
    if len(sys.argv) < 2:
        return
        
    params = dict(arg.split("=") for arg in sys.argv[1].split("&"))
    action = params.get('action', '')
    
    # Handle TMDB actions
    if action == 'tmdb':
        tmdb = TMDBHelper()
        content_type = params.get('type', '')
        category = params.get('category', '')
        
        if content_type and category:
            items = tmdb.get_items(content_type, category)
            if items:
                # Create a directory window
                handle = int(sys.argv[1])
                xbmcplugin.setContent(handle, 'movies' if content_type == 'movies' else 'tvshows')
                
                # Add items to the directory
                for item in items:
                    list_item = xbmcgui.ListItem(label=item['title'])
                    list_item.setInfo('video', {
                        'title': item['title'],
                        'year': item['year'],
                        'plot': item['plot'],
                        'rating': item['rating'],
                        'mediatype': item['mediatype']
                    })
                    list_item.setArt({
                        'poster': item['poster'],
                        'fanart': item['fanart']
                    })
                    # Add playable flag and context menu
                    list_item.setProperty('IsPlayable', 'true')
                    url = f'plugin://plugin.video.themoviedb.helper?info=play&tmdb_id={item["tmdb_id"]}&type={content_type}'
                    xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=list_item, isFolder=False)
                
                # End directory listing
                xbmcplugin.endOfDirectory(handle)

if __name__ == '__main__':
    main()