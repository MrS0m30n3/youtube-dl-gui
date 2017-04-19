# youtube-dlG

A cross platform front-end GUI of the popular [youtube-dl](http://rg3.github.io/youtube-dl/) media downloader, written in wxPython. [List of supported sites](https://rg3.github.io/youtube-dl/supportedsites.html).

## Screenshots

**Main window**

![Youtube-dl-gui main window](http://i.imgur.com/I4oXPWs.png)

**Options window**

![Options window](http://i.imgur.com/eShdoLD.png)

## Installation

**Linux (from source):** `sudo python setup.py install`

**Linux (Ubuntu PPA):** http://ppa.launchpad.net/nilarimogard/webupd8/ubuntu/pool/main/y/youtube-dlg/ (TODO: update)

**Linux (Arch AUR):** https://aur.archlinux.org/packages/youtube-dl-gui-git/ (TODO: update)

**Linux (Slackware SlackBuild):** https://slackbuilds.org/repository/14.2/network/youtube-dl-gui/

**Windows:** TODO Package MSI/portable ZIP

**Mac:** TODO Package app

Then you can call youtube-dlg from the command line, using the `youtube-dl-gui` command, or by creating a desktop launcher (TODO)

## Contributing

**Support for new language:** See [Localization HOWTO](locale_build/HOWTO.md).

**Reporting bugs:** See [Issues](https://github.com/MrS0m30n3/youtube-dl-gui/issues).


## Requirements
[Python](http://www.python.org) 2.7+, [wxPython](http://wxpython.org) 2.9.1+, [twodict](https://pypi.python.org/pypi/twodict/1.2), [FFMPEG & FFPROBE](http://www.ffmpeg.org) (optional, to convert video files to audio-only files).

## Authors

See [AUTHORS](AUTHORS) file
      
## License

The [Public Domain License](LICENSE)

## Thanks

Thanks to youtube-dl authors for creating such an amazing tool.

## Frequently Asked Questions

 * **Post processing takes a long time**: There should be no post-processing if you leave the video format to default (which defaults to the best format) and did not check convert to audio or embed subtitles, otherwise the file will be re-encoded to the format you selected (which takes time/CPU resources).
 
 * **The website I'm trying to download from is not supported**: youtube-dl-gui uses [youtube-dl](https://github.com/rg3/youtube-dl) in the backend to download files. youtube-dl provides a list of [extractors](https://github.com/rg3/youtube-dl/tree/master/youtube_dl/extractor) to work with each particular site. If you'd like to request support for a new website, please submit it to youtube-dl's [issue tracker](https://github.com/rg3/youtube-dl/issues).
 
 * **How do I change the naming pattern for downloaded files?**: See [this comment](https://github.com/MrS0m30n3/youtube-dl-gui/issues/144#issuecomment-263195019)
