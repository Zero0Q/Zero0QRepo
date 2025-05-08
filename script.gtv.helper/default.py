import sys
import xbmc
import xbmcaddon
import xbmcgui
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
                # Create a window to display items
                window = xbmcgui.Window(10000)
                window.setProperty('GTV.TMDB.Items', items)
                xbmc.executebuiltin('Container.Refresh')

if __name__ == '__main__':
    main()