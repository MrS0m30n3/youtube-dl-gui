# youtube-dlG
A cross platform front-end GUI of the popular [youtube-dl](https://rg3.github.io/youtube-dl/) media downloader written in wxPython. [Supported sites](https://rg3.github.io/youtube-dl/supportedsites.html)

## Screenshots
![youtube-dl-gui main window](https://i.imgur.com/tMTtgPt.png)

## Requirements
* [Python 2.7.3+](https://www.python.org/downloads)
* [wxPython 3](https://wxpython.org/download.php)
* [TwoDict](https://pypi.python.org/pypi/twodict)
* [FFmpeg](https://ffmpeg.org/download.html) (optional, to post process video files)

## Downloads
* [Source (.zip)](https://github.com/MrS0m30n3/youtube-dl-gui/archive/0.3.8.zip)
* [Source (.tar.gz)](https://github.com/MrS0m30n3/youtube-dl-gui/archive/0.3.8.tar.gz)
* [PyPi](https://pypi.python.org/pypi/youtube-dlg/0.3.8)
* [Ubuntu PPA](http://ppa.launchpad.net/nilarimogard/webupd8/ubuntu/pool/main/y/youtube-dlg/)
* [Arch AUR](https://aur.archlinux.org/packages/youtube-dl-gui-git/)
* [Slackware SlackBuild](https://slackbuilds.org/repository/14.2/network/youtube-dl-gui/)
* [Windows Installer](https://github.com/MrS0m30n3/youtube-dl-gui/releases/download/0.3.8/youtube-dl-gui-0.3.8-win-setup.zip)
* [Windows Portable](https://github.com/MrS0m30n3/youtube-dl-gui/releases/download/0.3.8/youtube-dl-gui-0.3.8-win-portable.zip)

## Installation

### Install From Source
1. Download & extract the source
2. Change directory into *youtube-dl-gui-0.3.8*
3. Run `python setup.py install`

### Install PyPi
1. Run `pip install youtube-dlg`

### Install Windows Installer
1. Download & extract the Windows installer
2. Run the `setup.exe` file

## Contributing
* **Add support for new language:** See [localization howto](docs/localiation_howto.md)
* **Report a bug:** See [issues](https://github.com/MrS0m30n3/youtube-dl-gui/issues)

## Authors
See [AUTHORS](AUTHORS) file
      
## License
The [Public Domain License](LICENSE)

## Thanks
Thanks to everyone who contributed to this project and to [@philipzae](https://github.com/philipzae) for designing the new UI layout.

---

## Frequently Asked Questions

 * **Post processing takes a long time**: There should be no post-processing if you leave the video format to default (which defaults to the best format) and did not check convert to audio or embed subtitles, otherwise the file will be re-encoded to the format you selected (which takes time/CPU resources).
 
 * **The website I'm trying to download from is not supported**: youtube-dl-gui uses [youtube-dl](https://github.com/rg3/youtube-dl) in the backend to download files. youtube-dl provides a list of [extractors](https://github.com/rg3/youtube-dl/tree/master/youtube_dl/extractor) to work with each particular site. If you'd like to request support for a new website, please submit it to youtube-dl's [issue tracker](https://github.com/rg3/youtube-dl/issues).
 
 * **How do I change the naming pattern for downloaded files?**: See [this comment](https://github.com/MrS0m30n3/youtube-dl-gui/issues/144#issuecomment-263195019)
 
 * **When is the next release coming?**: youtube-dl-gui does not have a release schedule, next release will come when it's ready.
 
 * **How can i log the youtube-dl debug output**: Just go to Options>Extra tab and enable the **Debug youtube-dl** option.
 
 * **I don't see my language in the available subtitles languages**: You can't see it because it's not there, feel free to open a new pull-request and add support for your language (it's literally one line of code you don't need years of experience).
 
 * **I'm on OS-X and i get 'No module named wx' error**: You need to install wxPython. If you have [homebrew](https://brew.sh/) installed you can just run: `brew install wxpython`
 
 * **Is there an option to change the maximum parallel downloads**: You can change the number of max parallel downloads by editing the 'workers_number' option in your settings.json file (~/.config/youtubedlg/settings.json). Note that you need to restart youtube-dl-gui for the changes to take place.
 
 * **Not all formats reported by youtube-dl -F are available in youtube-dl-gui**: Unfortunately it is not possible to support all the video formats that youtube-dl provides. If you want to use a "custom" format you can follow this steps:
   1. Set the download format to *default*
   2. Go to Options>Extra tab
   3. Add `-f your_custom_format` in the commands box
   4. Download your video as you would normally do
   
 * **How can i use a youtube-dl option that's not available in youtube-dl-gui**: You can add extra youtube-dl command line options in the commands box under the Options>Extra tab.
 
 * **Can i download only the subtitles file**: If the video file is presented youtube-dl-gui will go ahead and download only the subtitles file else you will have to use youtube-dl or a different tool since youtube-dl-gui can't download only subtitles.
 
 * **I'm using the HLS downloader and i don't see any progress report**: That's a known issue you should use the native HLS implementation by enabling the **Prefer Native HLS** option under the Options>Extra tab. Note that the native HLS implementation might not work on every site. For more info you can read issue #49.
 
 * **I'm using the HLS downloader and the Stop button won't work**: That's also a known issue with the HLS downloader on Windows. You should use the native HLS implementation or wait for the download to complete normally. For more info you can read issue #49.
