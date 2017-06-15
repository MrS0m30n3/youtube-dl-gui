# Frequently Asked Questions

* **Post processing takes too long**:
There should be no post-processing if you leave the video format to default (which defaults to the best format) and did not check convert to audio or embed subtitles, otherwise the file will be re-encoded to the format you selected (which takes time/CPU resources).

* **The website I'm trying to download from is not supported**:
Youtube-dl-gui uses [youtube-dl](https://github.com/rg3/youtube-dl) in the backend to download files. Youtube-dl provides a list of [extractors](https://github.com/rg3/youtube-dl/tree/master/youtube_dl/extractor) to work with each particular site. If you'd like to request support for a new website, please submit it to youtube-dl's [issue tracker](https://github.com/rg3/youtube-dl/issues).

* **How do I change the naming pattern for downloaded files?**:
You can change the naming pattern by picking a different filename format under the Options>General tab. You can also use a custom pattern by setting the option to "Custom" and editing the output template field. For more infomations on the output template see [youtube-dl's output template section](https://github.com/rg3/youtube-dl/blob/master/README.md#output-template).

* **When is the next release coming?**:
Youtube-dl-gui does not have a release schedule, next release will come when it's ready.

* **How can i log the youtube-dl's debug output?**:
Just go to Options>Extra tab and enable the "Debug youtube-dl" option.

* **I don't see my language in the available subtitles languages**:
You can't see it because it's not there, feel free to open a new pull-request and add support for your language (it's literally one line of code you don't need years of experience).

* **I'm on OS-X and i get 'No module named wx' error**:
You need to install wxPython. If you have [homebrew](https://brew.sh/) installed you can just run: `brew install wxpython`

* **Is there an option to change the maximum parallel downloads?**:
You can change the number of max parallel downloads by editing the "workers_number" option in your settings.json file. Note that you need to restart youtube-dl-gui for the changes to take place.

  settings.json file location:
  * Windows: `%appdata%\youtube-dlg\settings.json`
  * Linux: `~/.config/youtube-dlg/settings.json`

* **Not all formats reported by youtube-dl '-F' are available in youtube-dl-gui**:
Unfortunately it is not possible to support all the video formats that youtube-dl provides. If you want to use a "custom"
format you can follow this steps:

  1. Set the download format to "default"
  2. Go to Options>Extra tab
  3. Add `-f your_custom_format` in the commands box
  4. Download your video as you would normally do

* **How can i use a youtube-dl option that's not available in youtube-dl-gui?**:
You can add extra youtube-dl command line options in the commands box under the Options>Extra tab.

* **Can i download only the subtitles file?**:
If the video file is presented youtube-dl-gui will go ahead and download only the subtitles file. If the video file is NOT presented you can add the `--skip-download` option, which will skip the video download phase. If you are not happy with the above options you should use a different tool for the job since youtube-dl-gui is not a subtitles downloader.

* **I'm using the HLS downloader and i don't see any progress report**:
That's a known issue you should use the native HLS implementation by enabling the "Prefer Native HLS" option under the Options>Extra tab. NOTE that the native HLS implementation **might not work on every site**. For more info you can read issue [#49](https://github.com/MrS0m30n3/youtube-dl-gui/issues/49).

* **I'm using the HLS downloader and the 'stop' button won't work**:
That's also a known issue with the HLS downloader on Windows. You should use the native HLS implementation or wait for the download to complete normally. For more info you can read issue [#49](https://github.com/MrS0m30n3/youtube-dl-gui/issues/49).

* **Is it possible to use a youtube-dl version other than the official one?**:
You can use your own version of youtube-dl by editing the "youtubedl_path" option in your settings.json file and make it point to your own binary (e.g. /usr/local/bin). Note that if youtube-dl-gui does not have write permissions to this new directory the "update" option in the GUI will fail. Also, note that changing the "youtubedl_path" won't change the update source which is hardcoded for now to "https://yt-dl.org/latest/".
