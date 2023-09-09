import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import os
import hashlib
import sqlite3

from PIL import Image, ImageEnhance
from contextlib import closing

try:
    import urllib2 as urllib
except ImportError:
    import urllib.request as urllib


OLD_IMAGE = ''
OLD_COLOR = ''

PY3 = True if sys.version_info.major == 3 else False

try:
    LOGNOTICE = xbmc.LOGNOTICE
except:
    LOGNOTICE = xbmc.LOGINFO
LOGWARNING = xbmc.LOGWARNING
LOGDEBUG = xbmc.LOGDEBUG
LOGERROR = xbmc.LOGERROR

ADDON = xbmcaddon.Addon()
ADDONID = ADDON.getAddonInfo('id')
ADDON_DATA_PATH = os.path.join(xbmcvfs.translatePath("special://profile/addon_data/%s" % ADDONID))
DATABASE = ADDON_DATA_PATH + "/colors.db"

USE_DB = True
DEBUG_MODE = False

def log(txt, loglevel=xbmc.LOGDEBUG):
    if isinstance(txt, str):
        if not PY3:
            txt = txt.decode("utf-8")
            message = u'%s: %s\n' % (ADDONID, txt)
            xbmc.log(msg=message.encode("utf-8"), level=loglevel)
        else:
            message = u'%s: %s\n' % (ADDONID, txt)
            xbmc.log(msg=message, level=loglevel)


class Main(xbmc.Monitor):

    def __init__(self):
        if USE_DB: self.createDatabase()
        self.start()

    def start(self):
        log('Service started', LOGNOTICE)

        while not self.abortRequested():
            self.getColor()

            self.waitForAbort(0.1)

    def createDatabase(self):
        try:
            if not os.path.exists(ADDON_DATA_PATH):
                os.makedirs(ADDON_DATA_PATH)
            with closing(sqlite3.connect(DATABASE)) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute("CREATE TABLE IF NOT EXISTS colors (id integer PRIMARY KEY, hash text NOT NULL, color text);")
        except Exception as e:
            log('Database error: Failed to open database or create table - %s' % (e), LOGERROR)

        return

    def lookupColor(self, hashval):
        try:
            with closing(sqlite3.connect(DATABASE)) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute("SELECT * FROM colors WHERE hash=?", (hashval,))
                    data = cursor.fetchall()
            return data
        except Exception as e:
            log('Database error: lookupColor failed %s' % e, LOGERROR)
            pass

        return []

    def storeColor(self, hashval, value):
        try:
            with closing(sqlite3.connect(DATABASE)) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute("INSERT INTO colors(hash,color) VALUES(?,?)", (hashval, value))
                    connection.commit()
            return
        except Exception as e:
            log('Database error: storeColor failed %s' % e, LOGERROR)
            pass

        return

    def removeColor(self, hashval):
        try:
            with closing(sqlite3.connect(DATABASE)) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute("DELETE FROM colors WHERE hash=?", (hashval, ))
            return
        except Exception as e:
            log('Database error: removeColor failed %s' % e, LOGERROR)
            pass

        return

    def getColor(self):
        global OLD_IMAGE

        # Get image from Kodi Control
        image = xbmc.getInfoLabel('Control.GetLabel(110000)')

        # If image has not changed then no nothing and return
        if image == OLD_IMAGE:
            return
        OLD_IMAGE = image

        # Get hash value of image
        hashval = hashlib.md5(image.encode("utf-8")).hexdigest()

        if USE_DB: 
            # Check database to see if color already exists
            val = self.lookupColor(hashval)
            if len(val) == 1:
                if not val[0][2]:
                    # Blank color found remove it from database and regenerate
                    self.removeColor(hashval)
                    # Generate new color
                    domColor = self.processImage(image, hashval)
                    # Store color in database
                    self.storeColor(hashval, domColor)
                    location="new"
                # Found color in database
                domColor = val[0][2]
                location = "database"
            else:
                # Generate new color
                domColor = self.processImage(image, hashval)
                # Store color in database
                self.storeColor(hashval, domColor)
                location="new"
        else:
                # Generate new color
                domColor = self.processImage(image, hashval)
                location="new"

        # Set window property with color
        window = xbmcgui.Window(10000)
        window.setProperty('GTV.color', domColor)
        window.setProperty('GTV.location', location)

    def processImage(self, image, hashval):
        global OLD_COLOR

        palettedata = [255, 0, 0, 255, 110, 0, 255, 220, 0, 178, 255, 0, 68, 255, 0, 0, 255, 42, 0, 255, 153, 0, 246, 255, 0, 136, 255, 0, 25, 255, 84, 0, 255, 195, 0, 255, 255, 0, 203, 255, 0, 93, 0, 0, 0, 255, 255, 255]

        try:
            # Open image and resize to make operations faster
            img = self.openImage(image)

            img.thumbnail((200, 200))

            # Enhance the saturation of the image
            enh = ImageEnhance.Color(img)
            img = enh.enhance(3)

            # Generate a new palette image
            palImage = Image.new('P',(16,16))
            palImage.putpalette(palettedata * 16)

            # Quantize the image down to the defined palette
            finalImg = self.quantize(img, palImage)

            if DEBUG_MODE:
                finalImg.save(ADDON_DATA_PATH + "/" + hashval + '.bmp')

            # Count the frequancy of the colors in the final quantized image
            palette = finalImg.getpalette()
            colorCounts = sorted(finalImg.getcolors(), reverse=True)
            colors = list()
            for i in range(len(colorCounts)):
                paletteIndex = colorCounts[i][1]
                domColor = palette[paletteIndex*3:paletteIndex*3+3]
                colors.append(tuple(domColor))

            # Choose the most used color that isn't black or white
            for col in colors:
                if col != (0,0,0) and col != (255,255,255):
                    outColor = col
                    break

            # format color to a hex string
            domColor = '%s%s%s' % (format(outColor[0], '02x'), format(outColor[1], '02x'), format(outColor[2], '02x'))
            OLD_COLOR = domColor

        except Exception as e:
            log('Color error: image: %s hash: %s error: %s' % (image, hashval, e), LOGERROR)

            # Any errors then just use the old color
            domColor = OLD_COLOR
            pass

        return domColor

    # Quantize to palette function
    # https://stackoverflow.com/questions/29433243/convert-image-to-specific-palette-using-pil-without-dithering
    def quantize(self, silf, palette):
        """Convert an RGB or L mode image to use a given P image's palette."""

        silf.load()

        # use palette from reference image
        palette.load()
        if palette.mode != "P":
            raise ValueError("bad mode for palette image")
        if silf.mode != "RGB" and silf.mode != "L":
            raise ValueError(
                "only RGB or L mode images can be quantized to a palette"
                )
        im = silf.im.convert("P", 0, palette.im)
        # the 0 above means turn OFF dithering

        # Later versions of Pillow (4.x) rename _makeself to _new
        try:
            return silf._new(im)
        except AttributeError:
            return silf._makeself(im)

    # Get cached image from Kodi
    # Code taken from script.embuary.helper authored by Sualfred
    # https://github.com/sualfred/script.embuary.helper/blob/leia/resources/lib/image.py
    def openImage(self, image):
        cachedImgPath = urllib.unquote(image.replace('image://', ''))
        if cachedImgPath.endswith('/'):
            cachedImgPath = cachedImgPath[:-1]

        cachedFiles = list()
        for path in [xbmc.getCacheThumbName(cachedImgPath), xbmc.getCacheThumbName(image)]:
            cachedFiles.append(os.path.join('special://profile/Thumbnails/', path[0], path[:-4] + '.jpg'))
            cachedFiles.append(os.path.join('special://profile/Thumbnails/', path[0], path[:-4] + '.png'))
            cachedFiles.append(os.path.join('special://profile/Thumbnails/Video/', path[0], path))

        for i in range(1,4):
            try:
                for cache in cachedFiles:
                    if xbmcvfs.exists(cache):
                        try:
                            img = Image.open(xbmc.translatePath(cache))
                            if DEBUG_MODE:
                                log('img=%s' % xbmc.translatePath(cache), LOGNOTICE)
                            return img

                        except Exception as error:
                            log('Image error: Failed to open cached image - %s' % error, LOGWARNING)

            except Exception as error:
                log('Image error: Failed to get image: %s - Error: %s' % (image, error), LOGERROR)
                pass

        return ''




if __name__ == '__main__':
    Main()