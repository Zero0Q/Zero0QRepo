# Zero0QRepo

A Kodi repository featuring the GTV skin and helper addons for a Google TV-like experience.

## Quick Installation

### Method 1: One-Click Install
1. Download [install-repo.strm](install-repo.strm)
2. Open the file in Kodi
3. The repository will install automatically

### Method 2: Direct URL Installation
1. In Kodi, go to Settings → File Manager
2. Click "Add source"
3. For the source path, enter: `https://raw.githubusercontent.com/Zero0Q/Zero0QRepo/master/`
4. Give it a name (e.g. "Zero0QRepo") and click OK
5. Go back to the home screen
6. Go to Add-ons
7. Click the package installer icon (top left)
8. Choose "Install from zip file"
9. Select "Zero0QRepo" and then select `repository.zero0qrepo-0.0.4.zip`

### Method 3: Quick Install URL
1. In Kodi, go to Settings → Add-ons
2. Enable "Unknown sources" if not already enabled
3. Copy this URL into a text editor on your device:
```
plugin://repository.zero0qrepo?install=true&url=https://github.com/Zero0Q/Zero0QRepo/raw/master/repository.zero0qrepo/repository.zero0qrepo-0.0.4.zip
```
4. Create a new text file and paste the URL into it
5. Save the file with a `.strm` extension (e.g. `install-repo.strm`)
6. In Kodi, browse to the `.strm` file and play it
7. Follow the prompts to install the repository

## Available Add-ons

- **GTV Skin** - A modern Kodi skin inspired by Google TV's interface
- **GTV Helper** - Helper script for the GTV skin with additional functionality

## Repository Structure

```
repository.zero0qrepo/      - Main repository addon
script.gtv.helper/         - GTV Helper script
skin.gtv/                 - GTV Skin
```

## License

GPL-2.0-or-later
