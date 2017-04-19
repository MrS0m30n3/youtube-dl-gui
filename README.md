# youtube-dlG

A cross platform front-end GUI of the popular [youtube-dl](http://rg3.github.io/youtube-dl/) media downloader, written in wxPython. [List of supported sites](https://rg3.github.io/youtube-dl/supportedsites.html).

## Screenshots

![youtube-dl-gui main window](https://i.imgur.com/tMTtgPt.png)

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

Thanks to everyone who contributed to this project and to [@philipzae](https://github.com/philipzae) for designing the new UI layout.

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
